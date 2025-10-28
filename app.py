from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from werkzeug.utils import secure_filename
from edi_parser import EDI837Parser
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'edi', 'x12', '837'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Parse the EDI file
        parser = EDI837Parser()
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        
        result = parser.parse_file(content)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if result['success']:
            summary_table = parser.get_summary_table()
            return jsonify({
                'success': True,
                'summary': summary_table,
                'segments': result['segments'],
                'raw_data': result['data'],
                'filename': filename
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'errors': result.get('errors', [])
            }), 400
    
    return jsonify({'error': 'Invalid file type. Please upload .txt, .edi, .x12, or .837 files'}), 400

@app.route('/parse_text', methods=['POST'])
def parse_text():
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'No EDI content provided'}), 400
    
    parser = EDI837Parser()
    result = parser.parse_file(data['content'])
    
    if result['success']:
        summary_table = parser.get_summary_table()
        return jsonify({
            'success': True,
            'summary': summary_table,
            'segments': result['segments'],
            'raw_data': result['data']
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Unknown error'),
            'errors': result.get('errors', [])
        }), 400

@app.route('/sample')
def sample():
    """Provide a sample EDI 837 for testing"""
    sample_edi = """ISA*00*          *00*          *ZZ*SUBMITTER      *ZZ*RECEIVER       *101127*1719*^*00501*000000905*0*P*:~GS*HC*SUBMITTER*RECEIVER*20101127*1719*1*X*005010X222A1~ST*837*0001*005010X222A1~BHT*0019*00*244579*20061015*1023*CH~NM1*41*2*PREMIER BILLING SERVICE*****46*TGJ23~PER*IC*CONTACT NAME*TE*7176149999~NM1*40*2*KEY INSURANCE COMPANY*****46*66783JJT~HL*1**20*1~PRV*BI*PXC*203BF0100Y~NM1*85*2*BEN KILDARE SERVICE*****XX*9876543210~N3*234 SEAWAY ST~N4*MIAMI*FL*33111~REF*EI*587654321~HL*2*1*22*0~SBR*P*18*******CI~NM1*IL*1*SMITH*JANE****MI*JS00111223333~N3*236 N MAIN ST~N4*MIAMI*FL*33413~DMG*D8*19430501*F~NM1*PR*2*KEY INSURANCE COMPANY*****PI*999996666~CLM*26463774*100***11:B:1*Y*A*Y*I~DTP*431*D8*20061003~REF*D9*17312345600006351~HI*BK:0340*BF:V7389~LX*1~SV1*HC:99213*40*UN*1***1~DTP*472*D8*20061003~SE*23*0001~GE*1*1~IEA*1*000000905~"""
    
    parser = EDI837Parser()
    result = parser.parse_file(sample_edi)
    
    if result['success']:
        summary_table = parser.get_summary_table()
        return jsonify({
            'success': True,
            'summary': summary_table,
            'segments': result['segments'],
            'raw_data': result['data'],
            'sample_content': sample_edi
        })
    else:
        return jsonify({
            'success': False,
            'error': result.get('error', 'Unknown error')
        }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)