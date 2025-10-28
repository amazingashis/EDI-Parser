"""
EDI 837 (5010) Parser
Supports X222, X223, X224 versions
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class EDISegment:
    """Represents a single EDI segment"""
    tag: str
    elements: List[str]
    raw: str

class EDI837Parser:
    """
    EDI 837 Health Care Claim (5010) Parser
    Supports X222/X223/X224 versions
    """
    
    def __init__(self):
        self.segments = []
        self.parsed_data = {}
        self.errors = []
        
        # EDI segment definitions for 837
        self.segment_definitions = {
            'ISA': 'Interchange Control Header',
            'GS': 'Functional Group Header',
            'ST': 'Transaction Set Header',
            'BHT': 'Beginning of Hierarchical Transaction',
            'NM1': 'Individual or Organizational Name',
            'N3': 'Party Location',
            'N4': 'Geographic Location',
            'REF': 'Reference Information',
            'PER': 'Administrative Communications Contact',
            'HL': 'Hierarchical Level',
            'PRV': 'Provider Information',
            'SBR': 'Subscriber Information',
            'PAT': 'Patient Information',
            'CLM': 'Claim Information',
            'DTP': 'Date or Time or Period',
            'CL1': 'Institutional Claim Code',
            'PWK': 'Paperwork',
            'CN1': 'Contract Information',
            'AMT': 'Monetary Amount Information',
            'HI': 'Health Care Diagnosis Code',
            'LX': 'Transaction Set Line Number',
            'SV1': 'Professional Service',
            'SV2': 'Institutional Service Line',
            'SV3': 'Dental Service',
            'DX': 'Diagnosis',
            'SE': 'Transaction Set Trailer',
            'GE': 'Functional Group Trailer',
            'IEA': 'Interchange Control Trailer'
        }
        
        # Entity type codes for NM1 segments
        self.entity_types = {
            '40': 'Receiver',
            '41': 'Submitter',
            '85': 'Billing Provider',
            '87': 'Pay-to Provider',
            'IL': 'Insured or Subscriber',
            'QC': 'Patient',
            'PR': 'Payer',
            'DN': 'Referring Provider',
            'P3': 'Primary Care Provider',
            '82': 'Rendering Provider'
        }
        
    def parse_file(self, file_content: str) -> Dict[str, Any]:
        """Parse EDI 837 file content"""
        try:
            # Clean and split the content
            content = file_content.strip().replace('\n', '').replace('\r', '')
            
            # Determine segment separator (usually ~ or newline)
            segment_separator = '~'
            if '~' not in content:
                segments = content.split('\n')
            else:
                segments = content.split('~')
            
            # Parse each segment
            for segment_raw in segments:
                if segment_raw.strip():
                    self._parse_segment(segment_raw.strip())
            
            # Extract structured data
            self._extract_structured_data()
            
            return {
                'success': True,
                'data': self.parsed_data,
                'segments': [{'tag': s.tag, 'elements': s.elements, 'description': self.segment_definitions.get(s.tag, 'Unknown')} for s in self.segments],
                'errors': self.errors
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'errors': self.errors
            }
    
    def _parse_segment(self, segment_raw: str):
        """Parse individual EDI segment"""
        if not segment_raw:
            return
            
        # Element separator is usually * or |
        element_separator = '*'
        if '*' not in segment_raw and '|' in segment_raw:
            element_separator = '|'
        
        elements = segment_raw.split(element_separator)
        tag = elements[0] if elements else ''
        
        segment = EDISegment(
            tag=tag,
            elements=elements[1:] if len(elements) > 1 else [],
            raw=segment_raw
        )
        
        self.segments.append(segment)
    
    def _extract_structured_data(self):
        """Extract structured data from parsed segments"""
        self.parsed_data = {
            'interchange_control': {},
            'functional_groups': [],
            'transaction_sets': [],
            'claims': [],
            'providers': [],
            'subscribers': [],
            'patients': []
        }
        
        current_transaction = None
        current_claim = None
        current_hierarchy_level = None
        
        for segment in self.segments:
            if segment.tag == 'ISA':
                self._parse_isa(segment)
            elif segment.tag == 'GS':
                self._parse_gs(segment)
            elif segment.tag == 'ST':
                current_transaction = self._parse_st(segment)
            elif segment.tag == 'BHT':
                self._parse_bht(segment, current_transaction)
            elif segment.tag == 'NM1':
                self._parse_nm1(segment)
            elif segment.tag == 'CLM':
                current_claim = self._parse_clm(segment)
            elif segment.tag == 'HL':
                current_hierarchy_level = self._parse_hl(segment)
            elif segment.tag == 'DTP':
                self._parse_dtp(segment)
            elif segment.tag == 'HI':
                self._parse_hi(segment, current_claim)
            elif segment.tag == 'SV1':
                self._parse_sv1(segment, current_claim)
    
    def _parse_isa(self, segment: EDISegment):
        """Parse ISA - Interchange Control Header"""
        if len(segment.elements) >= 16:
            self.parsed_data['interchange_control'] = {
                'authorization_qualifier': segment.elements[0],
                'authorization_info': segment.elements[1],
                'security_qualifier': segment.elements[2],
                'security_info': segment.elements[3],
                'sender_id_qualifier': segment.elements[4],
                'sender_id': segment.elements[5],
                'receiver_id_qualifier': segment.elements[6],
                'receiver_id': segment.elements[7],
                'date': segment.elements[8],
                'time': segment.elements[9],
                'repetition_separator': segment.elements[10],
                'version': segment.elements[11],
                'control_number': segment.elements[12],
                'acknowledgment_requested': segment.elements[13],
                'usage_indicator': segment.elements[14],
                'component_separator': segment.elements[15]
            }
    
    def _parse_gs(self, segment: EDISegment):
        """Parse GS - Functional Group Header"""
        if len(segment.elements) >= 8:
            fg = {
                'functional_id_code': segment.elements[0],
                'application_sender_code': segment.elements[1],
                'application_receiver_code': segment.elements[2],
                'date': segment.elements[3],
                'time': segment.elements[4],
                'group_control_number': segment.elements[5],
                'responsible_agency_code': segment.elements[6],
                'version': segment.elements[7]
            }
            self.parsed_data['functional_groups'].append(fg)
    
    def _parse_st(self, segment: EDISegment):
        """Parse ST - Transaction Set Header"""
        if len(segment.elements) >= 2:
            ts = {
                'transaction_set_id': segment.elements[0],
                'control_number': segment.elements[1]
            }
            self.parsed_data['transaction_sets'].append(ts)
            return ts
        return None
    
    def _parse_bht(self, segment: EDISegment, transaction):
        """Parse BHT - Beginning of Hierarchical Transaction"""
        if len(segment.elements) >= 6 and transaction:
            transaction.update({
                'hierarchical_structure_code': segment.elements[0],
                'transaction_set_purpose_code': segment.elements[1],
                'reference_identification': segment.elements[2],
                'date': segment.elements[3],
                'time': segment.elements[4],
                'transaction_type_code': segment.elements[5]
            })
    
    def _parse_nm1(self, segment: EDISegment):
        """Parse NM1 - Individual or Organizational Name"""
        if len(segment.elements) >= 3:
            entity_type = segment.elements[0]
            entity_type_desc = self.entity_types.get(entity_type, f'Unknown ({entity_type})')
            
            name_info = {
                'entity_type_code': entity_type,
                'entity_type_description': entity_type_desc,
                'entity_type_qualifier': segment.elements[1] if len(segment.elements) > 1 else '',
                'name_last_or_organization': segment.elements[2] if len(segment.elements) > 2 else '',
                'name_first': segment.elements[3] if len(segment.elements) > 3 else '',
                'name_middle': segment.elements[4] if len(segment.elements) > 4 else '',
                'name_prefix': segment.elements[5] if len(segment.elements) > 5 else '',
                'name_suffix': segment.elements[6] if len(segment.elements) > 6 else '',
                'id_code_qualifier': segment.elements[7] if len(segment.elements) > 7 else '',
                'id_code': segment.elements[8] if len(segment.elements) > 8 else ''
            }
            
            if entity_type in ['85', '87', 'DN', 'P3', '82']:
                self.parsed_data['providers'].append(name_info)
            elif entity_type == 'IL':
                self.parsed_data['subscribers'].append(name_info)
            elif entity_type == 'QC':
                self.parsed_data['patients'].append(name_info)
    
    def _parse_clm(self, segment: EDISegment):
        """Parse CLM - Claim Information"""
        if len(segment.elements) >= 2:
            claim = {
                'claim_id': segment.elements[0],
                'claim_amount': segment.elements[1],
                'place_of_service': segment.elements[4] if len(segment.elements) > 4 else '',
                'provider_signature_indicator': segment.elements[5] if len(segment.elements) > 5 else '',
                'assignment_plan_participation': segment.elements[6] if len(segment.elements) > 6 else '',
                'benefits_assignment_indicator': segment.elements[7] if len(segment.elements) > 7 else '',
                'release_of_information_code': segment.elements[8] if len(segment.elements) > 8 else '',
                'diagnosis_codes': [],
                'service_lines': []
            }
            self.parsed_data['claims'].append(claim)
            return claim
        return None
    
    def _parse_hl(self, segment: EDISegment):
        """Parse HL - Hierarchical Level"""
        if len(segment.elements) >= 3:
            return {
                'hierarchical_id': segment.elements[0],
                'parent_hierarchical_id': segment.elements[1],
                'hierarchical_level_code': segment.elements[2],
                'hierarchical_child_code': segment.elements[3] if len(segment.elements) > 3 else ''
            }
        return None
    
    def _parse_dtp(self, segment: EDISegment):
        """Parse DTP - Date or Time or Period"""
        if len(segment.elements) >= 3:
            return {
                'date_qualifier': segment.elements[0],
                'date_format_qualifier': segment.elements[1],
                'date': segment.elements[2]
            }
        return None
    
    def _parse_hi(self, segment: EDISegment, claim):
        """Parse HI - Health Care Diagnosis Code"""
        if claim and len(segment.elements) >= 1:
            # Parse diagnosis codes
            for element in segment.elements:
                if element and ':' in element:
                    qualifier, code = element.split(':', 1)
                    claim['diagnosis_codes'].append({
                        'qualifier': qualifier,
                        'code': code
                    })
    
    def _parse_sv1(self, segment: EDISegment, claim):
        """Parse SV1 - Professional Service"""
        if claim and len(segment.elements) >= 2:
            service_line = {
                'procedure_code': segment.elements[0],
                'charge_amount': segment.elements[1],
                'unit_of_measure': segment.elements[2] if len(segment.elements) > 2 else '',
                'service_unit_count': segment.elements[3] if len(segment.elements) > 3 else '',
                'place_of_service': segment.elements[4] if len(segment.elements) > 4 else ''
            }
            claim['service_lines'].append(service_line)

    def get_summary_table(self) -> List[Dict[str, Any]]:
        """Generate summary table data for web display"""
        summary = []
        
        # Interchange Control
        if self.parsed_data.get('interchange_control'):
            ic = self.parsed_data['interchange_control']
            summary.append({
                'Section': 'Interchange Control',
                'Field': 'Sender ID',
                'Value': ic.get('sender_id', ''),
                'Description': 'EDI Interchange Sender Identification'
            })
            summary.append({
                'Section': 'Interchange Control',
                'Field': 'Receiver ID',
                'Value': ic.get('receiver_id', ''),
                'Description': 'EDI Interchange Receiver Identification'
            })
            summary.append({
                'Section': 'Interchange Control',
                'Field': 'Date',
                'Value': ic.get('date', ''),
                'Description': 'Interchange Date'
            })
            summary.append({
                'Section': 'Interchange Control',
                'Field': 'Version',
                'Value': ic.get('version', ''),
                'Description': 'EDI Version (X222/X223/X224)'
            })
        
        # Claims
        for i, claim in enumerate(self.parsed_data.get('claims', [])):
            summary.append({
                'Section': f'Claim {i+1}',
                'Field': 'Claim ID',
                'Value': claim.get('claim_id', ''),
                'Description': 'Patient Account Number'
            })
            summary.append({
                'Section': f'Claim {i+1}',
                'Field': 'Claim Amount',
                'Value': claim.get('claim_amount', ''),
                'Description': 'Total Claim Charge Amount'
            })
            summary.append({
                'Section': f'Claim {i+1}',
                'Field': 'Place of Service',
                'Value': claim.get('place_of_service', ''),
                'Description': 'Place of Service Code'
            })
        
        # Providers
        for i, provider in enumerate(self.parsed_data.get('providers', [])):
            summary.append({
                'Section': f'Provider {i+1}',
                'Field': 'Entity Type',
                'Value': provider.get('entity_type_description', ''),
                'Description': f"Provider Type ({provider.get('entity_type_code', '')})"
            })
            summary.append({
                'Section': f'Provider {i+1}',
                'Field': 'Name',
                'Value': f"{provider.get('name_first', '')} {provider.get('name_last_or_organization', '')}".strip(),
                'Description': 'Provider Name'
            })
            summary.append({
                'Section': f'Provider {i+1}',
                'Field': 'ID',
                'Value': provider.get('id_code', ''),
                'Description': f"Provider ID ({provider.get('id_code_qualifier', '')})"
            })
        
        # Subscribers
        for i, subscriber in enumerate(self.parsed_data.get('subscribers', [])):
            summary.append({
                'Section': f'Subscriber {i+1}',
                'Field': 'Name',
                'Value': f"{subscriber.get('name_first', '')} {subscriber.get('name_last_or_organization', '')}".strip(),
                'Description': 'Subscriber Name'
            })
            summary.append({
                'Section': f'Subscriber {i+1}',
                'Field': 'ID',
                'Value': subscriber.get('id_code', ''),
                'Description': f"Subscriber ID ({subscriber.get('id_code_qualifier', '')})"
            })
        
        # Patients
        for i, patient in enumerate(self.parsed_data.get('patients', [])):
            summary.append({
                'Section': f'Patient {i+1}',
                'Field': 'Name',
                'Value': f"{patient.get('name_first', '')} {patient.get('name_last_or_organization', '')}".strip(),
                'Description': 'Patient Name'
            })
            summary.append({
                'Section': f'Patient {i+1}',
                'Field': 'ID',
                'Value': patient.get('id_code', ''),
                'Description': f"Patient ID ({patient.get('id_code_qualifier', '')})"
            })
        
        return summary