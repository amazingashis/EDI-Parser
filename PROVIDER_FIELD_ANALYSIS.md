# EDI 837 Provider Field Analysis with Primary Care Provider (PCP) Support

## Overview
EDI 837 contains multiple provider-related fields across different segments. Based on EDI 834 enrollment standards, Primary Care Provider (PCP) information is also supported in EDI 837 transactions.

## Provider Field Categories

### 1. Provider Identification Fields (NM1 Segments)

#### Billing Provider (NM1*85)
- **Purpose**: Entity responsible for billing
- **Fields**:
  - `NM103`: Organization/Last Name
  - `NM104`: First Name (if individual)
  - `NM108`: ID Code Qualifier (XX=NPI, EI=EIN, etc.)
  - `NM109`: Provider ID/NPI

#### Rendering Provider (NM1*82) 
- **Purpose**: Provider who actually rendered the service
- **Fields**:
  - `NM103`: Provider Last Name/Organization
  - `NM104`: First Name
  - `NM108`: ID Code Qualifier
  - `NM109`: Provider ID/NPI

#### Referring Provider (NM1*DN)
- **Purpose**: Provider who referred the patient
- **Fields**:
  - `NM103`: Referring Provider Name
  - `NM108`: ID Code Qualifier
  - `NM109`: Provider ID/NPI

#### **Primary Care Provider (NM1*P3)** 🏥
- **Purpose**: Patient's assigned Primary Care Provider (from EDI 834)
- **Fields**:
  - `NM103`: PCP Last Name/Organization
  - `NM104`: PCP First Name
  - `NM108`: ID Code Qualifier
  - `NM109`: PCP ID/NPI
- **Usage**: Links to patient's enrolled PCP from 834 enrollment

#### Pay-to Provider (NM1*87)
- **Purpose**: Entity to receive payment
- **Fields**:
  - `NM103`: Pay-to Provider Name
  - `NM108`: ID Code Qualifier  
  - `NM109`: Provider ID/NPI

### 2. Provider Specialty Information (PRV Segment)

#### PRV Segment Fields
- **PRV01**: Provider Code
  - `BI` = Billing Provider
  - `RF` = Referring Provider  
  - `AT` = Attending Provider
  - `PE` = Performing Provider
  - `PC` = Primary Care Provider
- **PRV02**: Reference ID Qualifier
  - `PXC` = Healthcare Provider Taxonomy (most common)
  - `ZZ` = Mutually Defined
- **PRV03**: Provider Taxonomy Code
  - Example: `207Q00000X` = Family Medicine
  - Example: `208D00000X` = General Practice
  - Example: `207R00000X` = Internal Medicine
- **PRV04**: State License (optional)
- **PRV05**: Provider Organization Type

### 3. Provider Address Information

#### N3/N4 Segments (following NM1 segments)
- **N3**: Address Lines
- **N4**: City, State, ZIP

#### Example Provider Address Chain:
```
NM1*85*2*MEDICAL GROUP*****XX*1234567890~
N3*123 MEDICAL CENTER BLVD~
N4*ANYTOWN*CA*12345~
PRV*BI*PXC*207Q00000X~
```

### 4. Provider Reference Information (REF Segments)

#### Common REF Qualifiers for Providers:
- **REF*EI**: Employer ID Number
- **REF*0B**: State License Number  
- **REF*1G**: Prior Authorization Number
- **REF*G2**: Provider UPIN
- **REF*LU**: Location Number
- **REF*TJ**: Federal Tax ID

### 5. Primary Care Provider (PCP) Integration with EDI 834

#### EDI 834 to EDI 837 PCP Linkage:
1. **EDI 834 Enrollment**: Patient enrolled with assigned PCP
2. **EDI 837 Claim**: References same PCP via NM1*P3 segment

#### PCP Field Mapping:
```
EDI 834 (Enrollment):
NM1*P3*1*SMITH*JOHN****XX*1234567890~  (PCP Assignment)

EDI 837 (Claim):
NM1*P3*1*SMITH*JOHN****XX*1234567890~  (Same PCP Reference)
PRV*PC*PXC*207Q00000X~                  (PCP Specialty)
```

### 6. Provider Hierarchy in EDI 837

#### Typical Provider Sequence:
1. **Billing Provider (85)** - Always required
2. **Pay-to Provider (87)** - If different from billing
3. **Rendering Provider (82)** - Who performed service
4. **Referring Provider (DN)** - If service was referred
5. **Primary Care Provider (P3)** - Patient's assigned PCP
6. **Attending Provider** - For facility claims

### 7. Healthcare Provider Taxonomy Codes (Key Specialties)

#### Primary Care Specialties:
- `207Q00000X`: Family Medicine
- `208D00000X`: General Practice  
- `207R00000X`: Internal Medicine
- `207KA0200X`: Adolescent Medicine
- `207PE0004X`: Emergency Medicine

#### Specialist Categories:
- `207X00000X`: Orthopaedic Surgery
- `207T00000X`: Neurological Surgery
- `208000000X`: Pediatrics
- `207Y00000X`: Otolaryngology

### 8. Provider Identification Best Practices

#### NPI (National Provider Identifier):
- **Format**: 10-digit numeric
- **Qualifier**: XX in NM108
- **Required**: For all provider types
- **Scope**: Individual and organizational providers

#### State License Integration:
- **REF*0B**: State license number
- **PRV04**: State code where licensed
- **Validation**: Cross-reference with PRV taxonomy

### 9. Implementation Notes

#### PCP Validation Rules:
1. PCP taxonomy must be primary care specialty
2. PCP NPI must match EDI 834 enrollment
3. PCP should be geographically accessible to patient
4. PCP assignment affects referral requirements

#### Provider Data Quality:
1. **Completeness**: All required NM1 fields populated
2. **Consistency**: Provider IDs consistent across segments  
3. **Validation**: Taxonomy codes valid for provider type
4. **Compliance**: NPI format and check digit validation

### 10. EDI 834 PCP Assignment Fields

#### Member-Level PCP Assignment:
```
NM1*IL*1*DOE*JANE****MI*MEMBER123~     (Member)
NM1*P3*1*SMITH*JOHN****XX*1234567890~  (Assigned PCP)
REF*18*PCP-EFFECTIVE-DATE~              (PCP Assignment Date)
```

This comprehensive provider field structure enables full tracking of provider relationships, specialties, and primary care assignments across the EDI 837/834 ecosystem.