from flask import Flask, request, render_template, make_response
import os
from converter import process_ipynb_files

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        uploaded_files = request.files.getlist('notebooks')
        saved_files = []

        for file in uploaded_files:
            if file.filename.endswith('.ipynb'):
                path = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(path)
                saved_files.append(path)

        print(f"Uploaded files: {saved_files}")

        if not saved_files:
            return make_response("No valid .ipynb files uploaded.", 400)

        final_pdf = process_ipynb_files(saved_files, upload_dir=UPLOAD_FOLDER, output_dir=OUTPUT_FOLDER)
        print(f"Final PDF saved at: {final_pdf}")

        filename = os.path.basename(final_pdf)

        # Check if the PDF exists and is not empty
        if not os.path.exists(final_pdf) or os.path.getsize(final_pdf) == 0:
            print(f"Error: The generated PDF is either missing or empty!")
            return make_response("Error: The generated PDF is missing or empty.", 500)

        # Try opening the PDF to ensure it's not corrupted
        try:
            with open(final_pdf, 'rb') as f:
                data = f.read()
        except Exception as e:
            print(f"Error reading the PDF: {e}")
            return make_response("Error reading the generated PDF.", 500)

        response = make_response(data)
        response.headers.set('Content-Type', 'application/pdf')
        response.headers.set('Content-Disposition', f'attachment; filename="{filename}"')
        return response

    except Exception as e:
        print(f"Error in upload route: {e}")
        return make_response(f"Internal server error: {e}", 500)

@app.route('/delete', methods=['POST'])
def delete_output():
    try:
        # Delete all files in output folder
        for file in os.listdir(OUTPUT_FOLDER):
            path = os.path.join(OUTPUT_FOLDER, file)
            if os.path.isfile(path):
                os.remove(path)
        return "Deleted", 200
    except Exception as e:
        print(f"Error deleting output file: {e}")
        return f"Failed to delete: {e}", 500

if __name__ == "__main__":
    # Run with debug=False to avoid double execution issues
    app.run(debug=False)
