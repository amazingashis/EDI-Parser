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
        
        # Detailed element definitions for each segment
        self.element_definitions = {
            'ISA': [
                {'pos': '01', 'name': 'Authorization Information Qualifier', 'description': 'Code to identify the type of information in the Authorization Information'},
                {'pos': '02', 'name': 'Authorization Information', 'description': 'Information used for additional identification or authorization'},
                {'pos': '03', 'name': 'Security Information Qualifier', 'description': 'Code to identify the type of information in the Security Information'},
                {'pos': '04', 'name': 'Security Information', 'description': 'Information used for identifying the security information about the interchange sender'},
                {'pos': '05', 'name': 'Interchange ID Qualifier', 'description': 'Qualifier to designate the system/method of code structure used to designate the sender'},
                {'pos': '06', 'name': 'Interchange Sender ID', 'description': 'Identification code published by the sender for other parties to use'},
                {'pos': '07', 'name': 'Interchange ID Qualifier', 'description': 'Qualifier to designate the system/method of code structure used to designate the receiver'},
                {'pos': '08', 'name': 'Interchange Receiver ID', 'description': 'Identification code published by the receiver for other parties to use'},
                {'pos': '09', 'name': 'Interchange Date', 'description': 'Date of the interchange'},
                {'pos': '10', 'name': 'Interchange Time', 'description': 'Time of the interchange'},
                {'pos': '11', 'name': 'Repetition Separator', 'description': 'Type is not applicable; the repetition separator is a delimiter'},
                {'pos': '12', 'name': 'Interchange Control Version Number', 'description': 'Code specifying the version number of the interchange control structure'},
                {'pos': '13', 'name': 'Interchange Control Number', 'description': 'A control number assigned by the interchange sender'},
                {'pos': '14', 'name': 'Acknowledgment Requested', 'description': 'Code sent by the sender to request an interchange acknowledgment'},
                {'pos': '15', 'name': 'Interchange Usage Indicator', 'description': 'Code to indicate whether data enclosed by this interchange envelope is test, production or information'}
            ],
            'GS': [
                {'pos': '01', 'name': 'Functional ID Code', 'description': 'Code identifying a group of application related transaction sets'},
                {'pos': '02', 'name': 'Application Sender Code', 'description': 'Code identifying party sending transmission'},
                {'pos': '03', 'name': 'Application Receiver Code', 'description': 'Code identifying party receiving transmission'},
                {'pos': '04', 'name': 'Date', 'description': 'Date expressed as CCYYMMDD'},
                {'pos': '05', 'name': 'Time', 'description': 'Time expressed in 24-hour clock time as follows: HHMM, or HHMMSS, or HHMMSSD, or HHMMSSDD'},
                {'pos': '06', 'name': 'Group Control Number', 'description': 'Assigned number originated and maintained by the sender'},
                {'pos': '07', 'name': 'Responsible Agency Code', 'description': 'Code used to identify the issuer of the standard'},
                {'pos': '08', 'name': 'Version / Release / Industry ID Code', 'description': 'Code indicating the version, release, subrelease, and industry identifier'}
            ],
            'ST': [
                {'pos': '01', 'name': 'Transaction Set ID Code', 'description': 'Code uniquely identifying a Transaction Set'},
                {'pos': '02', 'name': 'Transaction Set Control Number', 'description': 'Identifying control number that must be unique within the transaction set functional group'},
                {'pos': '03', 'name': 'Implementation Convention Reference', 'description': 'Reference assigned to identify a specific implementation convention'}
            ],
            'BHT': [
                {'pos': '01', 'name': 'Hierarchical Structure Code', 'description': 'Code indicating the hierarchical application structure of a transaction set'},
                {'pos': '02', 'name': 'Transaction Set Purpose Code', 'description': 'Code identifying purpose of transaction set'},
                {'pos': '03', 'name': 'Reference Identification', 'description': 'Reference information as defined for a particular Transaction Set'},
                {'pos': '04', 'name': 'Date', 'description': 'Date expressed as CCYYMMDD'},
                {'pos': '05', 'name': 'Time', 'description': 'Time expressed in 24-hour clock time'},
                {'pos': '06', 'name': 'Transaction Type Code', 'description': 'Code specifying the type of transaction'}
            ],
            'NM1': [
                {'pos': '01', 'name': 'Entity ID Code', 'description': 'Code identifying an organizational entity, a physical location, property or an individual'},
                {'pos': '02', 'name': 'Entity Type Qualifier', 'description': 'Code qualifying the entity'},
                {'pos': '03', 'name': 'Name Last or Organization Name', 'description': 'Individual last name or organizational name'},
                {'pos': '04', 'name': 'Name First', 'description': 'Individual first name'},
                {'pos': '05', 'name': 'Name Middle', 'description': 'Individual middle name or initial'},
                {'pos': '06', 'name': 'Name Prefix', 'description': 'Prefix to individual name'},
                {'pos': '07', 'name': 'Name Suffix', 'description': 'Suffix to individual name'},
                {'pos': '08', 'name': 'ID Code Qualifier', 'description': 'Code designating the system/method of code structure used for Identification Code'},
                {'pos': '09', 'name': 'ID Code', 'description': 'Code identifying a party or other code'}
            ],
            'CLM': [
                {'pos': '01', 'name': 'Claim Submitter Identifier', 'description': 'Unique claim identifier assigned by the claim submitter'},
                {'pos': '02', 'name': 'Monetary Amount', 'description': 'Total claim charge amount'},
                {'pos': '03', 'name': 'Claim Filing Indicator Code', 'description': 'Code identifying the type of claim'},
                {'pos': '04', 'name': 'Non-Institutional Claim Type Code', 'description': 'Code identifying the type of claim for non-institutional providers'},
                {'pos': '05', 'name': 'Health Care Service Location Information', 'description': 'Information about the location where healthcare services were provided'},
                {'pos': '06', 'name': 'Provider Accept Assignment Code', 'description': 'Code indicating whether the provider accepts assignment'},
                {'pos': '07', 'name': 'Assignment Claim Participation Code', 'description': 'Code indicating the provider participation in assignment'},
                {'pos': '08', 'name': 'Benefits Assignment Certification Indicator', 'description': 'Code indicating benefits assignment certification'},
                {'pos': '09', 'name': 'Release of Information Code', 'description': 'Code indicating the release of information'}
            ],
            'SV1': [
                {'pos': '01', 'name': 'Procedure Code', 'description': 'Procedure code and modifiers'},
                {'pos': '02', 'name': 'Monetary Amount', 'description': 'Line item charge amount'},
                {'pos': '03', 'name': 'Unit of Measure Code', 'description': 'Code specifying the units in which a value is being expressed'},
                {'pos': '04', 'name': 'Service Unit Count', 'description': 'Number of units of service'},
                {'pos': '05', 'name': 'Place of Service Code', 'description': 'Code identifying the place where the service was performed'},
                {'pos': '06', 'name': 'Service Type Code', 'description': 'Code identifying the type of service'},
                {'pos': '07', 'name': 'Composite Diagnosis Code Pointer', 'description': 'Reference to diagnosis codes'}
            ],
            'HI': [
                {'pos': '01', 'name': 'Health Care Code Information', 'description': 'Code information for health care diagnosis, procedure, etc.'}
            ],
            'DTP': [
                {'pos': '01', 'name': 'Date Time Qualifier', 'description': 'Code specifying type of date or time or both date and time'},
                {'pos': '02', 'name': 'Date Time Period Format Qualifier', 'description': 'Code indicating the date format, time format, or date and time format'},
                {'pos': '03', 'name': 'Date Time Period', 'description': 'Expression of a date, a time, or range of dates, times or dates and times'}
            ]
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
                'segments': [self._parse_segment_elements(s) for s in self.segments],
                'detailed_segments': [self._get_detailed_segment_info(s) for s in self.segments],
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

    def get_data_summary(self) -> Dict[str, Any]:
        """Generate comprehensive data summary for statistics display"""
        # Common procedure code descriptions for reference
        procedure_descriptions = {
            # CPT Codes - Evaluation and Management
            '99213': 'Office/Outpatient Visit - Est Patient (15 min)',
            '99214': 'Office/Outpatient Visit - Est Patient (25 min)',
            '99215': 'Office/Outpatient Visit - Est Patient (40 min)',
            '99203': 'Office/Outpatient Visit - New Patient (30 min)',
            '99204': 'Office/Outpatient Visit - New Patient (45 min)',
            '99205': 'Office/Outpatient Visit - New Patient (60 min)',
            '99212': 'Office/Outpatient Visit - Est Patient (10 min)',
            '99211': 'Office/Outpatient Visit - Est Patient (5 min)',
            
            # Laboratory Tests
            '85025': 'Complete Blood Count (CBC) with Differential',
            '80053': 'Comprehensive Metabolic Panel',
            '85027': 'Complete Blood Count (CBC)',
            '36415': 'Venipuncture for Blood Collection',
            '81001': 'Urinalysis',
            '85610': 'Prothrombin Time (PT)',
            '85730': 'Partial Thromboplastin Time (PTT)',
            
            # Radiology
            '71020': 'Chest X-ray, 2 views',
            '73060': 'Knee X-ray, 2 views',
            '74177': 'CT Abdomen and Pelvis with Contrast',
            '72148': 'MRI Lumbar Spine without Contrast',
            '76700': 'Abdominal Ultrasound',
            
            # Procedures
            '45378': 'Diagnostic Colonoscopy',
            '43239': 'Upper Endoscopy (EGD)',
            '12001': 'Simple Repair of Superficial Wounds',
            '29881': 'Arthroscopy, Knee',
            '58661': 'Laparoscopy, Surgical',
            
            # Preventive Care
            'G0439': 'Annual Wellness Visit',
            'G0438': 'Annual Wellness Visit - Initial',
            'Q0091': 'Screening Papanicolaou Smear',
            'G0202': 'Screening Mammography',
            
            # HCPCS Codes
            'J3420': 'Injection, Vitamin B-12',
            'A4253': 'Blood Glucose Test Strips',
            'E0110': 'Crutches, Forearm',
            'L3806': 'Wrist Hand Finger Orthosis',
        }
        
        summary = {
            'counts': {},
            'amounts': {},
            'details': {},
            'coverage': {},
            'procedure_analysis': {}
        }
        
        # Count basic entities
        summary['counts']['total_claims'] = len(self.parsed_data.get('claims', []))
        summary['counts']['total_providers'] = len(self.parsed_data.get('providers', []))
        summary['counts']['total_subscribers'] = len(self.parsed_data.get('subscribers', []))
        summary['counts']['total_patients'] = len(self.parsed_data.get('patients', []))
        summary['counts']['total_segments'] = len(self.segments)
        
        # Calculate financial amounts and procedure analysis
        total_claim_amount = 0
        total_service_amount = 0
        service_lines_count = 0
        procedure_amounts = {}  # Track amounts by procedure code
        procedure_counts = {}   # Track frequency by procedure code
        
        for claim in self.parsed_data.get('claims', []):
            # Claim amounts
            if claim.get('claim_amount'):
                try:
                    total_claim_amount += float(claim['claim_amount'])
                except (ValueError, TypeError):
                    pass
            
            # Service line amounts and procedure analysis
            for service in claim.get('service_lines', []):
                service_lines_count += 1
                charge_amount = 0
                
                if service.get('charge_amount'):
                    try:
                        charge_amount = float(service['charge_amount'])
                        total_service_amount += charge_amount
                    except (ValueError, TypeError):
                        pass
                
                # Analyze procedure codes with amounts
                proc_code = service.get('procedure_code', '')
                if proc_code:
                    # Extract code type and main code
                    if ':' in proc_code:
                        code_type, main_code = proc_code.split(':', 1)
                    else:
                        code_type = 'UNKNOWN'
                        main_code = proc_code
                    
                    # Track procedure amounts and counts
                    if main_code not in procedure_amounts:
                        procedure_amounts[main_code] = {
                            'total_amount': 0,
                            'count': 0,
                            'code_type': code_type,
                            'description': procedure_descriptions.get(main_code, f'Procedure Code {main_code}')
                        }
                    
                    procedure_amounts[main_code]['total_amount'] += charge_amount
                    procedure_amounts[main_code]['count'] += 1
                    procedure_counts[main_code] = procedure_counts.get(main_code, 0) + 1
        
        summary['amounts']['total_claim_amount'] = total_claim_amount
        summary['amounts']['total_service_amount'] = total_service_amount
        summary['amounts']['average_claim_amount'] = (
            total_claim_amount / summary['counts']['total_claims'] 
            if summary['counts']['total_claims'] > 0 else 0
        )
        summary['counts']['total_service_lines'] = service_lines_count
        
        # Enhanced procedure analysis
        summary['procedure_analysis']['by_amount'] = procedure_amounts
        summary['procedure_analysis']['total_procedures'] = len(procedure_amounts)
        
        # Top procedures by amount
        top_by_amount = sorted(
            procedure_amounts.items(), 
            key=lambda x: x[1]['total_amount'], 
            reverse=True
        )[:10]
        summary['procedure_analysis']['top_by_amount'] = top_by_amount
        
        # Top procedures by frequency
        top_by_frequency = sorted(
            procedure_amounts.items(), 
            key=lambda x: x[1]['count'], 
            reverse=True
        )[:10]
        summary['procedure_analysis']['top_by_frequency'] = top_by_frequency
        
        # Provider details
        provider_types = {}
        for provider in self.parsed_data.get('providers', []):
            ptype = provider.get('entity_type_description', 'Unknown')
            provider_types[ptype] = provider_types.get(ptype, 0) + 1
        summary['details']['provider_types'] = provider_types
        
        # Service details (keeping original structure for compatibility)
        diagnosis_codes = []
        
        for claim in self.parsed_data.get('claims', []):
            # Diagnosis codes
            for diag in claim.get('diagnosis_codes', []):
                if diag.get('code'):
                    diagnosis_codes.append(diag['code'])
        
        summary['details']['procedure_codes'] = procedure_counts
        summary['details']['diagnosis_codes'] = list(set(diagnosis_codes))  # Unique codes
        summary['counts']['unique_procedures'] = len(procedure_counts)
        summary['counts']['unique_diagnoses'] = len(set(diagnosis_codes))
        
        # Transaction details
        ic = self.parsed_data.get('interchange_control', {})
        summary['details']['sender_id'] = ic.get('sender_id', '')
        summary['details']['receiver_id'] = ic.get('receiver_id', '')
        summary['details']['interchange_date'] = ic.get('date', '')
        summary['details']['version'] = ic.get('version', '')
        
        # Segment analysis
        segment_counts = {}
        for segment in self.segments:
            segment_counts[segment.tag] = segment_counts.get(segment.tag, 0) + 1
        summary['details']['segment_distribution'] = segment_counts
        
        # Data quality metrics
        total_elements = 0
        populated_elements = 0
        
        for segment in self.segments:
            total_elements += len(segment.elements)
            populated_elements += sum(1 for el in segment.elements if el.strip())
        
        summary['coverage']['total_elements'] = total_elements
        summary['coverage']['populated_elements'] = populated_elements
        summary['coverage']['population_rate'] = (
            (populated_elements / total_elements * 100) if total_elements > 0 else 0
        )
        
        return summary

    def _parse_segment_elements(self, segment: EDISegment) -> Dict[str, Any]:
        """Parse segment elements with basic info"""
        return {
            'tag': segment.tag,
            'elements': segment.elements,
            'description': self.segment_definitions.get(segment.tag, 'Unknown segment'),
            'raw': segment.raw
        }

    def _get_detailed_segment_info(self, segment: EDISegment) -> Dict[str, Any]:
        """Get detailed element-level information for a segment"""
        element_definitions = self.element_definitions.get(segment.tag, [])
        
        detailed_elements = []
        for i, element_value in enumerate(segment.elements):
            element_position = f"{i+1:02d}"  # Format as 01, 02, etc.
            
            # Find element definition
            element_def = None
            for definition in element_definitions:
                if definition['pos'] == element_position:
                    element_def = definition
                    break
            
            if element_def:
                element_info = {
                    'position': element_position,
                    'name': element_def['name'],
                    'value': element_value,
                    'description': element_def['description'],
                    'is_present': bool(element_value.strip()) if element_value else False
                }
            else:
                element_info = {
                    'position': element_position,
                    'name': f'Element {element_position}',
                    'value': element_value,
                    'description': 'Element definition not available',
                    'is_present': bool(element_value.strip()) if element_value else False
                }
            
            # Add special processing for certain elements
            if segment.tag == 'ISA':
                element_info = self._enhance_isa_element(element_position, element_value, element_info)
            elif segment.tag == 'NM1':
                element_info = self._enhance_nm1_element(element_position, element_value, element_info)
            
            detailed_elements.append(element_info)
        
        return {
            'segment_tag': segment.tag,
            'segment_name': self.segment_definitions.get(segment.tag, 'Unknown segment'),
            'elements': detailed_elements,
            'raw_segment': segment.raw,
            'element_count': len(segment.elements)
        }

    def _enhance_isa_element(self, position: str, value: str, element_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance ISA segment elements with specific values"""
        enhancements = {
            '01': {  # Authorization Information Qualifier
                '00': 'No Authorization Information Present (No Meaningful Information in I02)',
                '03': 'Additional Data Identification'
            },
            '03': {  # Security Information Qualifier
                '00': 'No Security Information Present (No Meaningful Information in I04)',
                '01': 'Password'
            },
            '05': {  # Interchange ID Qualifier (Sender)
                'ZZ': 'Mutually Defined',
                '01': 'Duns (Dun & Bradstreet)',
                '14': 'Duns Plus Suffix',
                '20': 'Health Industry Number',
                '27': 'Carrier Identification Number',
                '28': 'Fiscal Intermediary Identification Number',
                '29': 'Medicare Provider and Supplier Identification Number',
                '30': 'U.S. Federal Tax Identification Number'
            },
            '07': {  # Interchange ID Qualifier (Receiver)
                'ZZ': 'Mutually Defined',
                '01': 'Duns (Dun & Bradstreet)',
                '14': 'Duns Plus Suffix',
                '20': 'Health Industry Number',
                '27': 'Carrier Identification Number',
                '28': 'Fiscal Intermediary Identification Number',
                '29': 'Medicare Provider and Supplier Identification Number',
                '30': 'U.S. Federal Tax Identification Number'
            },
            '12': {  # Interchange Control Version Number
                '00501': 'Standards Approved for Publication by ASC X12 Procedures Review Board through October 2003'
            },
            '14': {  # Acknowledgment Requested
                '0': 'No Interchange Acknowledgment Requested',
                '1': 'Interchange Acknowledgment Requested'
            },
            '15': {  # Interchange Usage Indicator
                'T': 'Test Data',
                'P': 'Production Data',
                'I': 'Information'
            }
        }
        
        if position in enhancements and value in enhancements[position]:
            element_info['interpreted_value'] = enhancements[position][value]
        
        return element_info

    def _enhance_nm1_element(self, position: str, value: str, element_info: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance NM1 segment elements with specific values"""
        if position == '01' and value in self.entity_types:
            element_info['interpreted_value'] = self.entity_types[value]
        elif position == '02':
            type_map = {
                '1': 'Person',
                '2': 'Non-Person Entity'
            }
            if value in type_map:
                element_info['interpreted_value'] = type_map[value]
        elif position == '08':
            qualifier_map = {
                'XX': 'Health Care Financing Administration National Provider Identifier',
                'PI': 'Payor Identification',
                'MI': 'Member Identification Number',
                'EI': 'Employer Identification Number',
                '46': 'Electronic Transmitter Identification Number'
            }
            if value in qualifier_map:
                element_info['interpreted_value'] = qualifier_map[value]
        
        return element_info