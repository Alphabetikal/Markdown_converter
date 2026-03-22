import re
import os
from flask import Flask, render_template, request, flash, redirect

app = Flask(__name__, template_folder='./')
app.secret_key = '1234445666'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.md'):
        flash('Only .md files are allowed!')
        return redirect('/')

    try:
        # Read the uploaded markdown file
        data = file.read().decode('utf-8')

        # Convert headers H1-H6
        for i in range(6, 0, -1):
            pattern = r'^' + '#' * i + r'\s+(.+)$'
            replace = fr'<h{i}>\1</h{i}>'
            data = re.sub(pattern, replace, data, flags=re.MULTILINE)

        # Bold text **text**
        data = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', data)

        # Italic text *text*
        data = re.sub(r'\*(.*?)\*', r'<em>\1</em>', data)

        # Inline code `code`
        data = re.sub(r'`(.*?)`', r'<span class="inline-code">\1</span>', data)

        # Wrap remaining lines in <div> if not empty or already a header/div
        lines = data.split('\n')
        new_lines = []
        for line in lines:
            if not line.strip():  # empty line
                new_lines.append('')
            elif re.match(r'^<h\d>.*</h\d>$', line) or re.match(r'^<div>.*</div>$', line):
                new_lines.append(line)
            else:
                new_lines.append(f'<div>{line}</div>')

        modified_data = '\n'.join(new_lines)

        # Save the HTML file
        output_filename = os.path.splitext(file.filename)[0] + '.html'
        output_path = os.path.join('uploads', output_filename)
        os.makedirs('uploads', exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as out_f:
            out_f.write(modified_data)

        flash(f"Markdown converted to HTML and saved as '{output_filename}' in uploads/")
        return redirect('/')

    except Exception as e:
        flash(f"Error processing file: {e}")
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)