"""
Universal EDI Parser (5010)
Supports multiple healthcare EDI transactions organized by layout:
- EDI 837 (Healthcare Claims) - Claims Layout
- EDI 820 (Payment Order/Remittance Advice) - Revenue Layout  
- EDI 834 (Benefit Enrollment and Maintenance) - Member Layout
Supports X222, X223, X224 versions for 837; 5010 versions for 820/834
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

class UniversalEDIParser:
    """
    Universal EDI Parser supporting healthcare transaction layouts:
    
    CLAIMS LAYOUT:
    - EDI 837: Health Care Claims (X222/X223/X224 versions)
    
    REVENUE LAYOUT: 
    - EDI 820: Payment Order/Remittance Advice (5010)
    
    MEMBER LAYOUT:
    - EDI 834: Benefit Enrollment and Maintenance (5010)
    """
    
    def __init__(self):
        self.segments = []
        self.parsed_data = {}
        self.errors = []
        self.transaction_type = None  # Will be determined during parsing
        
        # Universal EDI segment definitions (837 + 820)
        self.segment_definitions = {
            # Common segments
            'ISA': 'Interchange Control Header',
            'GS': 'Functional Group Header',
            'ST': 'Transaction Set Header',
            'BHT': 'Beginning of Hierarchical Transaction',
            'NM1': 'Individual or Organizational Name',
            'N3': 'Party Location',
            'N4': 'Geographic Location',
            'REF': 'Reference Information',
            'PER': 'Administrative Communications Contact',
            'DTP': 'Date or Time or Period',
            'AMT': 'Monetary Amount Information',
            'SE': 'Transaction Set Trailer',
            'GE': 'Functional Group Trailer',
            'IEA': 'Interchange Control Trailer',
            
            # EDI 837 specific segments
            'HL': 'Hierarchical Level',
            'PRV': 'Provider Information',
            'SBR': 'Subscriber Information',
            'PAT': 'Patient Information',
            'CLM': 'Claim Information',
            'CL1': 'Institutional Claim Code',
            'PWK': 'Paperwork',
            'CN1': 'Contract Information',
            'HI': 'Health Care Diagnosis Code',
            'LX': 'Transaction Set Line Number',
            'SV1': 'Professional Service',
            'SV2': 'Institutional Service Line',
            'SV3': 'Dental Service',
            'DX': 'Diagnosis',
            
            # EDI 820 specific segments (Revenue Layout)
            'TRN': 'Trace',
            'CUR': 'Currency',
            'RMR': 'Remittance Advice',
            'DTM': 'Date/Time Reference',
            'N1': 'Name',
            'N2': 'Additional Name Information',
            'ENT': 'Entity',
            'ADX': 'Adjustment',
            'PLB': 'Provider Level Adjustment',
            'SVC': 'Service Payment Information',
            'CAS': 'Claims Adjustment',
            'QTY': 'Quantity',
            'LQ': 'Industry Code',
            'FTX': 'Free Text',
            'BPR': 'Beginning Segment for Payment Order/Remittance Advice',
            'TED': 'Technical Error Description',
            'SCH': 'Line Item Schedule',
            
            # EDI 834 specific segments (Member Layout)
            'BGN': 'Beginning Segment',
            'QTY': 'Quantity Information',
            'N1': 'Party Identification',
            'INS': 'Member Level Detail',
            'COB': 'Coordination of Benefits',
            'DSB': 'Disability Information',
            'HD': 'Health Coverage',
            'DX': 'Diagnosis',
            'ICM': 'Member Income',
            'LS': 'Loop Header',
            'LE': 'Loop Trailer',
            'LUI': 'Language Use',
            'EC': 'Employment Class',
            'EMS': 'Employment Status',
            'SSE': 'Entry and Exit Information'
        }
        
        # Entity type codes for NM1 segments (837 + 820)
        self.entity_types = {
            # Common entity types
            '40': 'Receiver',
            '41': 'Submitter',
            'PR': 'Payer',
            
            # EDI 837 specific entity types
            '85': 'Billing Provider',
            '87': 'Pay-to Provider',
            'IL': 'Insured or Subscriber',
            'QC': 'Patient',
            'DN': 'Referring Provider',
            'P3': 'Primary Care Provider',
            '82': 'Rendering Provider',
            
            # EDI 820 specific entity types (Revenue Layout)
            'PE': 'Payee',
            'TT': 'Third Party Administrator',
            'GP': 'Group',
            'BO': 'Broker or Sales Office',
            'FA': 'Facility',
            'LI': 'Limited Partner',
            'SJ': 'Service Organization',
            'PT': 'Patient',
            'QD': 'Responsible Party',
            'QN': 'Credit Recipient',
            'TL': 'Training Location',
            'VN': 'Vendor',
            'X3': 'Dependent',
            
            # EDI 834 specific entity types (Member Layout)
            'P5': 'Plan Sponsor',
            'IN': 'Insurer',
            'BO': 'Broker',
            'TV': 'Third Party Administrator',
            'P6': 'Third Party Administrator',
            'GP': 'Gateway Provider',
            'Y2': 'Employer',
            'ZZ': 'Mutually Defined',
            'S1': 'Submitter',
            'R1': 'Receiver',
            'C1': 'Member',
            'E1': 'Employee',
            'D1': 'Dependent',
            'S2': 'Spouse',
            'DX': 'Dependent',
            '19': 'Child',
            '53': 'Life Partner'
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
            ],
            # EDI 820 specific element definitions
            'BPR': [
                {'pos': '01', 'name': 'Transaction Handling Code', 'description': 'Code designating the action to be taken by all parties'},
                {'pos': '02', 'name': 'Monetary Amount', 'description': 'Total payment amount'},
                {'pos': '03', 'name': 'Credit/Debit Flag Code', 'description': 'Code indicating whether amount is credit or debit'},
                {'pos': '04', 'name': 'Payment Method Code', 'description': 'Code identifying the payment method'},
                {'pos': '05', 'name': 'Payment Format Code', 'description': 'Code identifying the payment format'},
                {'pos': '06', 'name': 'DFI ID Number Qualifier', 'description': 'Code identifying the Depository Financial Institution'},
                {'pos': '07', 'name': 'DFI Identification Number', 'description': 'Depository Financial Institution routing number'},
                {'pos': '08', 'name': 'Account Number Qualifier', 'description': 'Code identifying the account number type'},
                {'pos': '09', 'name': 'Account Number', 'description': 'Account number'},
                {'pos': '10', 'name': 'Originating Company Identifier', 'description': 'Company identifier for ACH transactions'},
                {'pos': '11', 'name': 'Originating Company Supplemental Code', 'description': 'Additional company identification'}
            ],
            'TRN': [
                {'pos': '01', 'name': 'Trace Type Code', 'description': 'Code identifying the type of trace number'},
                {'pos': '02', 'name': 'Reference Identification', 'description': 'Reference information for trace'},
                {'pos': '03', 'name': 'Originating Company Identifier', 'description': 'Company that originated the trace'},
                {'pos': '04', 'name': 'Reference Identification', 'description': 'Additional reference information'}
            ],
            'RMR': [
                {'pos': '01', 'name': 'Reference Identification Qualifier', 'description': 'Code qualifying the reference identification'},
                {'pos': '02', 'name': 'Reference Identification', 'description': 'Reference identification number'},
                {'pos': '03', 'name': 'Payment Action Code', 'description': 'Code indicating the payment action'},
                {'pos': '04', 'name': 'Monetary Amount', 'description': 'Payment amount'},
                {'pos': '05', 'name': 'Monetary Amount', 'description': 'Adjustment amount'},
                {'pos': '06', 'name': 'Monetary Amount', 'description': 'Outstanding balance'}
            ],
            'SVC': [
                {'pos': '01', 'name': 'Product/Service ID Qualifier', 'description': 'Code identifying the product/service'},
                {'pos': '02', 'name': 'Monetary Amount', 'description': 'Line item charge amount'},
                {'pos': '03', 'name': 'Monetary Amount', 'description': 'Line item payment amount'},
                {'pos': '04', 'name': 'Revenue Code', 'description': 'Revenue code for institutional claims'},
                {'pos': '05', 'name': 'Quantity', 'description': 'Service quantity'},
                {'pos': '06', 'name': 'Product/Service ID Qualifier', 'description': 'Bundled service identification'},
                {'pos': '07', 'name': 'Quantity', 'description': 'Approved service quantity'}
            ],
            'CAS': [
                {'pos': '01', 'name': 'Claim Adjustment Group Code', 'description': 'Code identifying the general category of adjustment'},
                {'pos': '02', 'name': 'Claim Adjustment Reason Code', 'description': 'Code identifying the reason for adjustment'},
                {'pos': '03', 'name': 'Monetary Amount', 'description': 'Adjustment amount'},
                {'pos': '04', 'name': 'Quantity', 'description': 'Adjustment quantity'},
                {'pos': '05', 'name': 'Claim Adjustment Reason Code', 'description': 'Second adjustment reason'},
                {'pos': '06', 'name': 'Monetary Amount', 'description': 'Second adjustment amount'}
            ],
            'PLB': [
                {'pos': '01', 'name': 'Reference Identification', 'description': 'Provider identifier'},
                {'pos': '02', 'name': 'Date', 'description': 'Fiscal period end date'},
                {'pos': '03', 'name': 'Reference Identification Qualifier', 'description': 'Adjustment identifier qualifier'},
                {'pos': '04', 'name': 'Reference Identification', 'description': 'Provider adjustment number'},
                {'pos': '05', 'name': 'Monetary Amount', 'description': 'Provider adjustment amount'}
            ],
            
            # EDI 834 specific element definitions (Member Layout)
            'BGN': [
                {'pos': '01', 'name': 'Transaction Set Purpose Code', 'description': 'Code identifying the purpose of the transaction set'},
                {'pos': '02', 'name': 'Reference Identification', 'description': 'Reference information for the transaction'},
                {'pos': '03', 'name': 'Date', 'description': 'Date expressed as CCYYMMDD'},
                {'pos': '04', 'name': 'Time', 'description': 'Time expressed in 24-hour clock time'},
                {'pos': '05', 'name': 'Time Zone Code', 'description': 'Code identifying the time zone'},
                {'pos': '06', 'name': 'Reference Identification', 'description': 'Original transaction reference'},
                {'pos': '07', 'name': 'Transaction Type Code', 'description': 'Code specifying the type of transaction'},
                {'pos': '08', 'name': 'Action Code', 'description': 'Code indicating the action to be taken'}
            ],
            'INS': [
                {'pos': '01', 'name': 'Member Indicator', 'description': 'Code indicating if person is a member or dependent'},
                {'pos': '02', 'name': 'Individual Relationship Code', 'description': 'Code indicating relationship to primary member'},
                {'pos': '03', 'name': 'Maintenance Type Code', 'description': 'Code identifying the maintenance action'},
                {'pos': '04', 'name': 'Maintenance Reason Code', 'description': 'Code identifying the reason for maintenance'},
                {'pos': '05', 'name': 'Benefit Status Code', 'description': 'Code identifying the benefit status'},
                {'pos': '06', 'name': 'Medicare Plan Code', 'description': 'Code identifying Medicare plan'},
                {'pos': '07', 'name': 'Eligibility Reason Code', 'description': 'Code identifying eligibility reason'},
                {'pos': '08', 'name': 'Employment Status Code', 'description': 'Code identifying employment status'},
                {'pos': '09', 'name': 'Student Status Code', 'description': 'Code identifying student status'},
                {'pos': '10', 'name': 'Handicap Indicator', 'description': 'Code indicating handicap status'},
                {'pos': '11', 'name': 'Date Time Period Format Qualifier', 'description': 'Code indicating date format'},
                {'pos': '12', 'name': 'Date Time Period', 'description': 'Date of death'},
                {'pos': '13', 'name': 'Confidentiality Code', 'description': 'Code indicating confidentiality level'},
                {'pos': '14', 'name': 'City Name', 'description': 'Birth city name'},
                {'pos': '15', 'name': 'State or Province Code', 'description': 'Birth state or province'},
                {'pos': '16', 'name': 'Country Code', 'description': 'Birth country code'},
                {'pos': '17', 'name': 'Number', 'description': 'Birth sequence number'}
            ],
            'HD': [
                {'pos': '01', 'name': 'Maintenance Type Code', 'description': 'Code indicating the maintenance action for coverage'},
                {'pos': '02', 'name': 'Maintenance Reason Code', 'description': 'Code indicating reason for maintenance'},
                {'pos': '03', 'name': 'Insurance Line Code', 'description': 'Code identifying the insurance line'},
                {'pos': '04', 'name': 'Plan Coverage Description', 'description': 'Description of plan coverage'},
                {'pos': '05', 'name': 'Coverage Level Code', 'description': 'Code indicating level of coverage'}
            ],
            'COB': [
                {'pos': '01', 'name': 'Payer Responsibility Sequence Number Code', 'description': 'Code indicating payer sequence'},
                {'pos': '02', 'name': 'Reference Identification', 'description': 'Member identification number'},
                {'pos': '03', 'name': 'Coordination of Benefits Code', 'description': 'Code indicating coordination of benefits'},
                {'pos': '04', 'name': 'Service Type Code', 'description': 'Code identifying the service type'}
            ],
            'ICM': [
                {'pos': '01', 'name': 'Frequency Code', 'description': 'Code indicating frequency of income'},
                {'pos': '02', 'name': 'Monetary Amount', 'description': 'Income amount'},
                {'pos': '03', 'name': 'Quantity', 'description': 'Number of periods'},
                {'pos': '04', 'name': 'Location Identifier', 'description': 'Income source location'},
                {'pos': '05', 'name': 'Salary Grade', 'description': 'Salary grade or level'}
            ]
        }
        
    def parse_file(self, file_content: str) -> Dict[str, Any]:
        """Parse EDI file content - supports both 837 and 820 transactions"""
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
            
            # Detect transaction type from ST segment
            self._detect_transaction_type()
            
            # Initialize data structure based on transaction type
            self._initialize_data_structure()
            
            # Extract structured data
            self._extract_structured_data()
            
            return {
                'success': True,
                'transaction_type': self.transaction_type,
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
    
    def _detect_transaction_type(self):
        """Detect the transaction type from ST segment"""
        for segment in self.segments:
            if segment.tag == 'ST' and len(segment.elements) >= 1:
                transaction_id = segment.elements[0]
                if transaction_id == '837':
                    self.transaction_type = '837'
                    break
                elif transaction_id == '820':
                    self.transaction_type = '820'
                    break
                elif transaction_id == '834':
                    self.transaction_type = '834'
                    break
        
        if not self.transaction_type:
            self.transaction_type = '837'  # Default to 837 for backward compatibility
    
    def _initialize_data_structure(self):
        """Initialize data structure based on transaction type and layout"""
        if self.transaction_type == '837':
            # Claims Layout
            self.parsed_data = {
                'layout': 'claims',
                'interchange_control': {},
                'functional_groups': [],
                'transaction_sets': [],
                'claims': [],
                'providers': [],
                'subscribers': [],
                'patients': []
            }
        elif self.transaction_type == '820':
            # Revenue Layout
            self.parsed_data = {
                'layout': 'revenue',
                'interchange_control': {},
                'functional_groups': [],
                'transaction_sets': [],
                'payment_info': {},
                'remittance_data': [],
                'payers': [],
                'payees': [],
                'adjustments': [],
                'service_payments': []
            }
        elif self.transaction_type == '834':
            # Member Layout
            self.parsed_data = {
                'layout': 'member',
                'interchange_control': {},
                'functional_groups': [],
                'transaction_sets': [],
                'transaction_info': {},
                'plan_sponsors': [],
                'insurers': [],
                'members': [],
                'dependents': [],
                'coverage_info': [],
                'employment_info': [],
                'income_info': []
            }
    
    def _extract_structured_data(self):
        """Extract structured data from parsed segments based on transaction type"""
        current_transaction = None
        current_claim = None
        current_hierarchy_level = None
        current_remittance = None
        
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
            elif segment.tag == 'DTP':
                self._parse_dtp(segment)
            
            # EDI 837 specific parsing
            if self.transaction_type == '837':
                if segment.tag == 'CLM':
                    current_claim = self._parse_clm(segment)
                elif segment.tag == 'HL':
                    current_hierarchy_level = self._parse_hl(segment)
                elif segment.tag == 'HI':
                    self._parse_hi(segment, current_claim)
                elif segment.tag == 'SV1':
                    self._parse_sv1(segment, current_claim)
            
            # EDI 820 specific parsing
            elif self.transaction_type == '820':
                if segment.tag == 'BPR':
                    self._parse_bpr(segment)
                elif segment.tag == 'TRN':
                    self._parse_trn(segment)
                elif segment.tag == 'RMR':
                    current_remittance = self._parse_rmr(segment)
                elif segment.tag == 'SVC':
                    self._parse_svc_820(segment)
                elif segment.tag == 'CAS':
                    self._parse_cas(segment)
                elif segment.tag == 'PLB':
                    self._parse_plb(segment)
    
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
        """Parse NM1 - Individual or Organizational Name (both 837 and 820)"""
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
            
            # Route to appropriate collection based on transaction type
            if self.transaction_type == '837':
                if entity_type in ['85', '87', 'DN', 'P3', '82']:
                    self.parsed_data['providers'].append(name_info)
                elif entity_type == 'IL':
                    self.parsed_data['subscribers'].append(name_info)
                elif entity_type == 'QC':
                    self.parsed_data['patients'].append(name_info)
            elif self.transaction_type == '820':
                if entity_type == 'PE':
                    self.parsed_data['payees'].append(name_info)
                elif entity_type == 'PR':
                    self.parsed_data['payers'].append(name_info)
    
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
    
    # EDI 820 specific parsing methods
    def _parse_bpr(self, segment: EDISegment):
        """Parse BPR - Beginning Segment for Payment Order/Remittance Advice"""
        if len(segment.elements) >= 4:
            self.parsed_data['payment_info'] = {
                'transaction_handling_code': segment.elements[0],
                'payment_amount': segment.elements[1],
                'credit_debit_flag': segment.elements[2],
                'payment_method': segment.elements[3],
                'payment_format': segment.elements[4] if len(segment.elements) > 4 else '',
                'dfi_qualifier': segment.elements[5] if len(segment.elements) > 5 else '',
                'dfi_identification': segment.elements[6] if len(segment.elements) > 6 else '',
                'account_qualifier': segment.elements[7] if len(segment.elements) > 7 else '',
                'account_number': segment.elements[8] if len(segment.elements) > 8 else '',
                'originating_company_id': segment.elements[9] if len(segment.elements) > 9 else '',
                'supplemental_code': segment.elements[10] if len(segment.elements) > 10 else ''
            }
    
    def _parse_trn(self, segment: EDISegment):
        """Parse TRN - Trace"""
        if len(segment.elements) >= 2:
            if 'trace_info' not in self.parsed_data:
                self.parsed_data['trace_info'] = []
            
            trace_info = {
                'trace_type_code': segment.elements[0],
                'reference_id': segment.elements[1],
                'originating_company_id': segment.elements[2] if len(segment.elements) > 2 else '',
                'reference_id_2': segment.elements[3] if len(segment.elements) > 3 else ''
            }
            self.parsed_data['trace_info'].append(trace_info)
    
    def _parse_rmr(self, segment: EDISegment):
        """Parse RMR - Remittance Advice"""
        if len(segment.elements) >= 4:
            remittance = {
                'reference_id_qualifier': segment.elements[0],
                'reference_id': segment.elements[1],
                'payment_action_code': segment.elements[2],
                'payment_amount': segment.elements[3],
                'adjustment_amount': segment.elements[4] if len(segment.elements) > 4 else '',
                'outstanding_balance': segment.elements[5] if len(segment.elements) > 5 else '',
                'service_payments': []
            }
            self.parsed_data['remittance_data'].append(remittance)
            return remittance
        return None
    
    def _parse_svc_820(self, segment: EDISegment):
        """Parse SVC - Service Payment Information (for EDI 820)"""
        if len(segment.elements) >= 3:
            service_payment = {
                'service_id_qualifier': segment.elements[0],
                'charge_amount': segment.elements[1],
                'payment_amount': segment.elements[2],
                'revenue_code': segment.elements[3] if len(segment.elements) > 3 else '',
                'service_quantity': segment.elements[4] if len(segment.elements) > 4 else '',
                'bundled_service_id': segment.elements[5] if len(segment.elements) > 5 else '',
                'approved_quantity': segment.elements[6] if len(segment.elements) > 6 else '',
                'adjustments': []
            }
            self.parsed_data['service_payments'].append(service_payment)
    
    def _parse_cas(self, segment: EDISegment):
        """Parse CAS - Claims Adjustment"""
        if len(segment.elements) >= 3:
            adjustment = {
                'group_code': segment.elements[0],
                'reason_code': segment.elements[1],
                'adjustment_amount': segment.elements[2],
                'adjustment_quantity': segment.elements[3] if len(segment.elements) > 3 else '',
                'reason_code_2': segment.elements[4] if len(segment.elements) > 4 else '',
                'adjustment_amount_2': segment.elements[5] if len(segment.elements) > 5 else ''
            }
            self.parsed_data['adjustments'].append(adjustment)
    
    def _parse_plb(self, segment: EDISegment):
        """Parse PLB - Provider Level Adjustment"""
        if len(segment.elements) >= 5:
            provider_adjustment = {
                'provider_id': segment.elements[0],
                'fiscal_period_date': segment.elements[1],
                'adjustment_id_qualifier': segment.elements[2],
                'adjustment_number': segment.elements[3],
                'adjustment_amount': segment.elements[4]
            }
            if 'provider_adjustments' not in self.parsed_data:
                self.parsed_data['provider_adjustments'] = []
            self.parsed_data['provider_adjustments'].append(provider_adjustment)

    def get_summary_table(self) -> List[Dict[str, Any]]:
        """Generate summary table data for web display (supports both 837 and 820)"""
        summary = []
        
        # Transaction type
        summary.append({
            'Section': 'Transaction Info',
            'Field': 'Transaction Type',
            'Value': f'EDI {self.transaction_type}',
            'Description': f'EDI {self.transaction_type} - {"Healthcare Claims" if self.transaction_type == "837" else "Payment Order/Remittance Advice"}'
        })
        
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
                'Description': 'EDI Version (X222/X223/X224 for 837, 5010 for 820)'
            })
        
        # EDI 837 specific sections
        if self.transaction_type == '837':
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
        
        # EDI 820 specific sections
        elif self.transaction_type == '820':
            # Payment Information
            if self.parsed_data.get('payment_info'):
                pi = self.parsed_data['payment_info']
                summary.append({
                    'Section': 'Payment Info',
                    'Field': 'Payment Amount',
                    'Value': pi.get('payment_amount', ''),
                    'Description': 'Total Payment Amount'
                })
                summary.append({
                    'Section': 'Payment Info',
                    'Field': 'Payment Method',
                    'Value': pi.get('payment_method', ''),
                    'Description': 'Payment Method Code'
                })
                summary.append({
                    'Section': 'Payment Info',
                    'Field': 'Credit/Debit',
                    'Value': pi.get('credit_debit_flag', ''),
                    'Description': 'Credit or Debit Flag'
                })
                summary.append({
                    'Section': 'Payment Info',
                    'Field': 'Account Number',
                    'Value': pi.get('account_number', ''),
                    'Description': 'Payment Account Number'
                })
            
            # Payers
            for i, payer in enumerate(self.parsed_data.get('payers', [])):
                summary.append({
                    'Section': f'Payer {i+1}',
                    'Field': 'Name',
                    'Value': f"{payer.get('name_first', '')} {payer.get('name_last_or_organization', '')}".strip(),
                    'Description': 'Payer Name'
                })
                summary.append({
                    'Section': f'Payer {i+1}',
                    'Field': 'ID',
                    'Value': payer.get('id_code', ''),
                    'Description': f"Payer ID ({payer.get('id_code_qualifier', '')})"
                })
            
            # Payees
            for i, payee in enumerate(self.parsed_data.get('payees', [])):
                summary.append({
                    'Section': f'Payee {i+1}',
                    'Field': 'Name',
                    'Value': f"{payee.get('name_first', '')} {payee.get('name_last_or_organization', '')}".strip(),
                    'Description': 'Payee Name'
                })
                summary.append({
                    'Section': f'Payee {i+1}',
                    'Field': 'ID',
                    'Value': payee.get('id_code', ''),
                    'Description': f"Payee ID ({payee.get('id_code_qualifier', '')})"
                })
            
            # Remittance Data
            for i, rmr in enumerate(self.parsed_data.get('remittance_data', [])):
                summary.append({
                    'Section': f'Remittance {i+1}',
                    'Field': 'Reference ID',
                    'Value': rmr.get('reference_id', ''),
                    'Description': 'Remittance Reference Identifier'
                })
                summary.append({
                    'Section': f'Remittance {i+1}',
                    'Field': 'Payment Amount',
                    'Value': rmr.get('payment_amount', ''),
                    'Description': 'Payment Amount for this Remittance'
                })
        
        return summary

    def get_data_summary(self) -> Dict[str, Any]:
        """Generate comprehensive data summary for statistics display (supports both 837 and 820)"""
        # Common procedure code descriptions for reference (837) and adjustment codes for 820
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
        
        # Adjustment reason codes for EDI 820
        adjustment_reason_codes = {
            '1': 'Deductible Amount',
            '2': 'Coinsurance Amount',
            '3': 'Co-payment Amount',
            '4': 'The procedure code is inconsistent with the modifier used or a required modifier is missing.',
            '5': 'The procedure code/bill type is inconsistent with the place of service.',
            '6': 'The procedure/revenue code is inconsistent with the patient\'s age.',
            '7': 'The procedure/revenue code is inconsistent with the patient\'s gender.',
            '8': 'The procedure code is inconsistent with the provider type/specialty.',
            '9': 'The diagnosis is inconsistent with the patient\'s age.',
            '10': 'The diagnosis is inconsistent with the patient\'s gender.',
            '11': 'The diagnosis is inconsistent with the procedure.',
            '12': 'The diagnosis is inconsistent with the provider type.',
            '13': 'The date of death precedes the date of service.',
            '14': 'The date of birth follows the date of service.',
            '15': 'The authorization number is missing, invalid, or does not apply to the billed services or provider.',
        }
        
        summary = {
            'counts': {},
            'amounts': {},
            'details': {},
            'coverage': {},
            'transaction_type': self.transaction_type
        }
        
        # Common counts
        summary['counts']['total_segments'] = len(self.segments)
        
        if self.transaction_type == '837':
            # EDI 837 specific analysis
            summary['procedure_analysis'] = {}
            
            # Count basic entities
            summary['counts']['total_claims'] = len(self.parsed_data.get('claims', []))
            summary['counts']['total_providers'] = len(self.parsed_data.get('providers', []))
            summary['counts']['total_subscribers'] = len(self.parsed_data.get('subscribers', []))
            summary['counts']['total_patients'] = len(self.parsed_data.get('patients', []))
            
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
            
            # Diagnosis codes
            diagnosis_codes = []
            for claim in self.parsed_data.get('claims', []):
                for diag in claim.get('diagnosis_codes', []):
                    if diag.get('code'):
                        diagnosis_codes.append(diag['code'])
            
            summary['details']['procedure_codes'] = procedure_counts
            summary['details']['diagnosis_codes'] = list(set(diagnosis_codes))  # Unique codes
            summary['counts']['unique_procedures'] = len(procedure_counts)
            summary['counts']['unique_diagnoses'] = len(set(diagnosis_codes))
        
        elif self.transaction_type == '820':
            # EDI 820 specific analysis
            summary['payment_analysis'] = {}
            summary['remittance_analysis'] = {}
            
            # Count basic entities
            summary['counts']['total_payers'] = len(self.parsed_data.get('payers', []))
            summary['counts']['total_payees'] = len(self.parsed_data.get('payees', []))
            summary['counts']['total_remittances'] = len(self.parsed_data.get('remittance_data', []))
            summary['counts']['total_service_payments'] = len(self.parsed_data.get('service_payments', []))
            summary['counts']['total_adjustments'] = len(self.parsed_data.get('adjustments', []))
            
            # Payment analysis
            payment_info = self.parsed_data.get('payment_info', {})
            if payment_info:
                try:
                    summary['amounts']['total_payment_amount'] = float(payment_info.get('payment_amount', 0))
                except (ValueError, TypeError):
                    summary['amounts']['total_payment_amount'] = 0
                
                summary['details']['payment_method'] = payment_info.get('payment_method', '')
                summary['details']['credit_debit_flag'] = payment_info.get('credit_debit_flag', '')
            else:
                summary['amounts']['total_payment_amount'] = 0
            
            # Remittance analysis
            total_remittance_amount = 0
            total_adjustment_amount = 0
            
            for rmr in self.parsed_data.get('remittance_data', []):
                try:
                    if rmr.get('payment_amount'):
                        total_remittance_amount += float(rmr['payment_amount'])
                    if rmr.get('adjustment_amount'):
                        total_adjustment_amount += float(rmr['adjustment_amount'])
                except (ValueError, TypeError):
                    pass
            
            summary['amounts']['total_remittance_amount'] = total_remittance_amount
            summary['amounts']['total_adjustment_amount'] = total_adjustment_amount
            
            # Adjustment analysis
            adjustment_types = {}
            adjustment_reasons = {}
            
            for adj in self.parsed_data.get('adjustments', []):
                group_code = adj.get('group_code', 'Unknown')
                reason_code = adj.get('reason_code', 'Unknown')
                
                adjustment_types[group_code] = adjustment_types.get(group_code, 0) + 1
                
                reason_desc = adjustment_reason_codes.get(reason_code, f'Code {reason_code}')
                adjustment_reasons[reason_desc] = adjustment_reasons.get(reason_desc, 0) + 1
            
            summary['details']['adjustment_types'] = adjustment_types
            summary['details']['adjustment_reasons'] = adjustment_reasons
            
            # Service payment analysis
            service_payment_total = 0
            for svc in self.parsed_data.get('service_payments', []):
                try:
                    if svc.get('payment_amount'):
                        service_payment_total += float(svc['payment_amount'])
                except (ValueError, TypeError):
                    pass
            
            summary['amounts']['total_service_payment_amount'] = service_payment_total
        
        # Common transaction details
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