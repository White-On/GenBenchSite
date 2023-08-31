from pathlib import Path
from genbenchsite.src.logger import logger

class Repository:
    def __init__(self, path):
        self.path = Path(path)
        self.file_list = []
        self.repository_list = []
        self.path.mkdir(parents=False, exist_ok=False)
    
    def __repr__(self):
        return f'Repository({self.path})\n' + \
            '\n'.join([f'├── {f}' for f in self.file_list]) + \
            '\n' + \
            '\n'.join([f'└── {r}' for r in self.repository_list]) 
    
    
    def add_file(self, file_name,content=''):
        self.file_list.append(file_name)
        with open(self.path / file_name, 'w') as f:
            f.write(content)
        return self
    
    def add_repository(self, repository_name):
        new_repository = Repository(self.path / repository_name)
        self.repository_list.append(new_repository)
        return new_repository

def load_config(path):
    # check that the file exists
    if not Path(path).exists():
        raise ValueError(f'{path} does not exists')
    config = ''
    section = ['config','task','target','theme']
    with open(path, 'r') as f:
        config = f.read()
    return { s:c for s,c in zip(section,config.split('|'))}

    

def create_template(target_path='benchmark_name',nb_targets=2,nb_themes=2,nb_tasks=2):
    # we look for the template file
    template_path = Path(__file__).parent / 'template.txt'
    logger.info(f'Loading template from {template_path}')
    config = load_config(template_path)
    logger.info(f'Creating benchmark template in {target_path}')
    # we check that no repository already exists
    if Path(target_path).exists():
        logger.error(f'{target_path} already exists')
        raise ValueError(f'The benchmark or directory {target_path} already exists, please choose another name')

    main_repo =  Repository(target_path)
    main_repo.add_repository('config').add_file('config.ini',content=config['config'])

    target_repo = main_repo.add_repository('targets')
    for i in range(nb_targets):
        target_repo.add_repository(f'target{i}').add_file('config.ini',content=f'[target{i}]\n' + config['target'])
    themes_repo = main_repo.add_repository('themes')
    for i in range(nb_themes):
        theme_repo = themes_repo.add_repository(f'theme{i}').add_file('theme.ini',content=f'[theme{i}]\n' + config['theme'])
        for j in range(nb_tasks):
            task_repo = (theme_repo.add_repository(f'task{j}')
                .add_file('config.ini',content=f'[task{i}]\n' + config['task'])
                .add_file('before_task.py',content='# This file is used to prepare the task\ndef before_task():\n    pass')
                .add_file('evaluation_task.py',content='# This file is executed to evaluate was has been done by the task\ndef evaluation_task():\n    pass')
            )
            for t in range(nb_targets):
                (task_repo
                    .add_file(f'target{t}_before_run.py',content='# This file is used to mesure the time before the task')
                    .add_file(f'target{t}_run.py',content='# This file is executed to run the task (runtime = run - before_run)')
                )
            task_repo.add_repository('data')
    return main_repo

if __name__ == '__main__':  
    print(create_template())
