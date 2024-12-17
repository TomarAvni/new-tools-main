import os
import sys
import subprocess
sys.path.append(r"C:\Users\prisma\solutions\personal\ariel\Open_mongo")
from flask import Flask, render_template, request, redirect, url_for, send_file
from psd_analyzer_2 import PSDAnalyzer

app = Flask(__name__)


# This is the open mongo - Ariel coding attempt
def run_mongo_analysis(mongo_file_path, save_path, client,  manual_or_auto, num_of_dofs, bin_size):

    print(f"Mongo File Path: {mongo_file_path}")
    print(f"save Path: {save_path}")
    print(f"client: {client}")
    print(f"monual or auto dofs : {manual_or_auto}")
    print(f"DOF List: {num_of_dofs}")
    print(f"Bin size: {bin_size}")

    if manual_or_auto == "Automatic top _ most active":
        updated_manual_or_auto = "False"
    else:
        updated_manual_or_auto = "True"

    venv_activate = r'C:\Users\prisma\solutions\.venv\Scripts\activate.bat'
    script_to_run = r'solutions\personal\ariel\Open_mongo\flask_main.py'

    command = (
        f'cmd /c "cd C:\\Users\\prisma && call {venv_activate} && '
        f'python {script_to_run} --mongo_file_path {mongo_file_path} '
        f'--save_path {save_path} --client {client} '
        f'--manual_or_auto_dofs {updated_manual_or_auto} --dofs {num_of_dofs} '
        f'--bin_size {bin_size} "'
    )

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    print(stdout.decode())
    print(stderr.decode())

def run_pd_tester(mongo_file_path, truth_table_path, save_path, site_name, dof_diff):
    dof_diff = int(dof_diff)


    print(f"Mongo File Path: {mongo_file_path}")
    print(f"Truth Table Path: {truth_table_path}")
    print(f"Save Path: {save_path}")
    print(f"Site Name: {site_name}")
    print(f"DOF Diff: {dof_diff}")

    venv_activate = r'C:\Users\prisma\solutions\.venv\Scripts\activate.bat'
    script_to_run = r'solutions\personal\ariel\PD_Tester\flask_main.py'

    command = (
        f'cmd /c "cd C:\\Users\\prisma && call {venv_activate} && '
        f'python {script_to_run} --mongo_file_path {mongo_file_path} '
        f'--truth_table_path {truth_table_path} --save_path {save_path} '
        f'--site_name {site_name} --dof_diff {dof_diff}"'
    )

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    print(stdout.decode())
    print(stderr.decode())

def run_gps_to_truthtable(folder_path, save_path, site_name, table_type):
    table_type = int(table_type)

    print(f"Folder Path: {folder_path}")
    print(f"Sanitized Save Path: {save_path}")
    print(f"Site Name: {site_name}")
    print(f"Table Type: {table_type}")

    venv_activate = r'C:\Users\prisma\solutions\.venv\Scripts\activate.bat'
    script_to_run = r'solutions\personal\ariel\GPS_logger_to_TruthTable\flask_main.py'

    command = (
        f'cmd /c "cd C:\\Users\\prisma && call {venv_activate} && '
        f'python {script_to_run} --folder_path {folder_path} --save_path {save_path}'
        f' --site_name {site_name} --truth_table_or_gps_table {table_type}"'
    )

    # Execute the command and capture output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    # Output the results for debugging
    print(stdout.decode())
    print(stderr.decode())

def run_prp_to_segy(folder_location, destination_folder, limit_duration):
    folder_location = folder_location.strip('"')
    destination_folder = destination_folder.strip('"')

    print(f"first quastion: {folder_location}")
    print(f"Destination Folder: {destination_folder} limit: {limit_duration}")

    baby_analyzer_path = r'C:\Users\Prisma\pz\microservices'

    command = (
        f'cmd /c "set PYTHONPATH={baby_analyzer_path} &&'   
        f' C:\\Users\\Prisma\\virtualenvs\\pzdev\\Scripts\\activate'
        f' && python -m baby_analyzer {folder_location} {destination_folder} -b segy'
        f' --file-limit-duration {limit_duration} --segy-max-workers 1"' # file size in sec
    )

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    print(stdout.decode())
    print(stderr.decode())


@app.route('/')
def home():
    return render_template('base.html')


@app.route('/TiTool', methods=['GET', 'POST'])
def TiTool():
    if request.method == 'POST':
        folder_path = request.form.get('folder_path')
        td_seconds = int(request.form.get('td_seconds', 1))
        low_freq = float(request.form.get('low_freq', 1))
        high_freq = float(request.form.get('high_freq', 30))
        n = int(request.form.get('n', 1800))

        if folder_path:
            analyzer = PSDAnalyzer(folder_path, td_seconds, low_freq, high_freq, n=n)
            plot_html, csv_file_path = analyzer.process(csv_file_path=os.path.join('static', 'psd_data.csv'))

            return render_template('TiTool.html', plot_html=plot_html, csv_file_path=csv_file_path)

    return render_template('TiTool.html')


@app.route('/plot')
def open_plot():
    folder_path = request.args.get('folder_path')
    td_seconds = int(request.args.get('td_seconds', 1))
    low_freq = float(request.args.get('low_freq', 1))
    high_freq = float(request.args.get('high_freq', 30))
    n = int(request.args.get('n', 1800))

    if folder_path:
        analyzer = PSDAnalyzer(folder_path, td_seconds, low_freq, high_freq, n=n)
        plot_html, _ = analyzer.process(export_csv=False)

        return render_template('plot_page.html', plot_html=plot_html)
    return "No plot data available."


@app.route('/download_csv')
def download_csv():
    csv_file_path = os.path.join('static', 'psd_data.csv')
    return send_file(csv_file_path, as_attachment=True)


@app.route('/prp_to_segy', methods=['GET', 'POST'])
def prp_to_segy():
    if request.method == 'POST':
        folder_location = request.form['folder_location']
        destination_folder = request.form['destination_folder']
        limit_duration = request.form['limit_duration']
        run_prp_to_segy(folder_location, destination_folder, limit_duration)
        return redirect(url_for('home'))

    return render_template('prp_to_segy.html')


@app.route('/gps_to_truthtable', methods=['GET', 'POST'])
def gps_to_truthtable():
    if request.method == 'POST':
        folder_path = request.form['folder_path']
        save_path = request.form['save_path']
        site_name = request.form['site_name']
        table_type = request.form['table_type']
        run_gps_to_truthtable(folder_path, save_path, site_name, table_type)
        return redirect(url_for('home'))

    return render_template('gps_to_truthtable.html')

@app.route('/pd_tester', methods=['GET', 'POST'])
def pd_tester():
    if request.method == 'POST':
        mongo_file_path = request.form.get('mongo_file_path')
        truth_table_path = request.form.get('truth_table_path')
        save_path = request.form.get('save_path')
        site_name = request.form.get('site_name')
        dof_diff = request.form.get('dof_diff')

        # Run the script
        run_pd_tester(mongo_file_path, truth_table_path, save_path, site_name, dof_diff)
        return redirect(url_for('home'))

    return render_template('pd_tester.html')

@app.route('/mongo_analysis', methods=['GET', 'POST'])
def mongo_analysis():
    if request.method == 'POST':
        mongo_file_path = request.form.get('mongo_file_path')
        save_path = request.form.get('save_path')
        dof_method = request.form.get('Dof_method')  # Radio
        dof_info = request.form.get('dof_input')
        bin_size = request.form.get('bin_size')
        client = request.form.get('client')  # Radio

        # Run the script
        run_mongo_analysis(mongo_file_path, save_path, client, dof_method, dof_info, bin_size)
        return redirect(url_for('home'))

    return render_template('mongo_analysis.html')


if __name__ == '__main__':
    app.run(host='10.50.0.41', port=3000, debug=False)
    