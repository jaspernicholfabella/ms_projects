#create jil files
import os

class JILCreate():
    name = ''
    python_file = ''
    description = ''
    output_dir = ''
    date_to_run = ''
    qa_start_time = ''
    prod_start_time = ''

    def __init__(self, **kwargs):
        try:
            self.name = kwargs['name']
            self.description = kwargs['description']
            self.python_file = kwargs['python_file']
            self.output_dir = kwargs['output_dir']
            self.qa_start_time = kwargs['qa_start_time']
            self.date_to_run = kwargs['date_to_run']
            self.prod_start_time = kwargs['prod_start_time']
        except Exception as e:
            print(e)

    def generate_jil(self):
        self.generate_jil_dev()
        self.generate_jil_qa()
        self.generate_jil_prod()

    def generate_jil_dev(self):
        jil_name = f'awpy-{self.name}'
        fp = open(f'{self.output_dir}{jil_name}-dev.jil', 'w')
        self.write_prefix(fp, jil_name, 'b')
        fp.write(f'description: "{self.description}"' + '\n')
        fp.write('\n')
        self.write_prefix(fp, f'{jil_name}-{self.python_file.replace(".py","")}', 'c')
        self.write_suffix(fp, jil_name, 'dev', runtype='-r')
        fp.close()

    def generate_jil_qa(self):
        jil_name = f'awpy-{self.name}'
        fp = open(f'{self.output_dir}{jil_name}-qa.jil', 'w')
        self.write_prefix(fp, jil_name, 'b')
        fp.write('date_conditions: 1' + '\n')
        fp.write(self.date_to_run + '\n')
        fp.write(f'start_times: "{self.qa_start_time}"' + '\n')
        fp.write(f'description: "{self.description}"' + '\n')
        fp.write('\n')
        self.write_prefix(fp, f'{jil_name}-{self.python_file.replace(".py","")}', 'c')
        self.write_suffix(fp, jil_name, 'qa')
        fp.close()

    def generate_jil_prod(self):
        jil_name = f'awpy-{self.name}'
        fp = open(f'{self.output_dir}{jil_name}-prod.jil', 'w')
        self.write_prefix(fp, jil_name, 'b')
        fp.write('date_conditions: 1' + '\n')
        fp.write(self.date_to_run + '\n')
        fp.write(f'start_times: "{self.prod_start_time}"' + '\n')
        fp.write(f'description: "{self.description}"' + '\n')
        fp.write('\n')
        self.write_prefix(fp, f'{jil_name}-{self.python_file.replace(".py","")}', 'c')
        self.write_suffix(fp, jil_name, 'prod')
        fp.close()

    def write_suffix(self, fp, jil_name, folder, runtype = ''):
        if runtype != '':
            run_type = ' ' + runtype
        else:
            run_type = ''
        fp.write(f'command: $PROJECTS_ROOT/projects/{self.name}/{self.python_file} -o $OUTDIR_ROOT/{self.name}/{run_type}'  + '\n')
        fp.write(f'description: "{self.description}"'  + '\n')
        fp.write('n_retrys: 3'  + '\n')
        fp.write(f'box_name: {jil_name}'  + '\n')
        fp.write(f'box_terminator: 1'  + '\n')
        fp.write('machine: awpy-vm'  + '\n')
        fp.write(f'std_out_file: ${{LOGDIR}}/{self.name}/$AUTO_JOB_NAME.`/bin/date +%Y%m%d`.out'  + '\n')
        fp.write(f'std_out_file: ${{LOGDIR}}/{self.name}/$AUTO_JOB_NAME.`/bin/date +%Y%m%d`.err'  + '\n')
        fp.write(f'profile: /ms/dist/eqr/PROJ/webdata-py/{folder}/config/{folder}/autosys.profile'  + '\n')

    @staticmethod
    def write_prefix(fp,  jil_name, job_type):
        fp.write(f'delete_job: {jil_name}'  + '\n')
        fp.write(f'insert_job: {jil_name}'  + '\n')
        fp.write(f'job_type: {job_type}'  + '\n')

