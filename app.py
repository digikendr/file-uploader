from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)

# Hardcoded AWS credentials and config for testing
AWS_ACCESS_KEY_ID = 'AKIA6G75DYUUCBTK76G7'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'
S3_BUCKET = 'digikendr'

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@app.route('/upload', methods=['POST'])
def upload_zip():
    # Ensure 'file' and 'filename' are present
    if 'file' not in request.files or 'filename' not in request.form:
        return jsonify({'error': 'Missing file or filename parameter'}), 400

    file = request.files['file']
    zip_filename = request.form['filename']

    if file.filename == '' or not zip_filename.endswith('.zip'):
        return jsonify({'error': 'Invalid file or filename'}), 400

    try:
        # Upload to S3
        s3_key = zip_filename
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            s3_key,
            ExtraArgs={'ContentType': 'application/zip'}
        )
        # Construct accessible URL
        url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

        return jsonify({'url': url}), 200

    except ClientError as e:
        app.logger.error(f"S3 upload failed: {e}")
        return jsonify({'error': 'Upload failed', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
