from pathlib import Path

class Repository:
    def __init__(self, path):
        self.path = Path(path)
        self.file_list = []
        self.repository_list = []
    
    def __repr__(self):
        return f'Repository({self.path})\n' + \
            '\n'.join([f'├── {f}' for f in self.file_list]) + \
            '\n' + \
            '\n'.join([f'└── {r}' for r in self.repository_list]) + \
    
    
    
    def add_file(self, file_name,content=''):
        self.file_list.append(file_name)
        # with open(self.path / file_name, 'w') as f:
        #     f.write(content)
        return self
    
    def add_repository(self, repository_name):
        new_repository = Repository(self.path / repository_name)
        self.repository_list.append(new_repository)
        return new_repository


def create_template(target_path):
    repo =  Repository(target_path)
    (repo.add_file('README.md')
        .add_file('LICENSE')
        .add_repository('src')
            .add_file('__init__.py')
            .add_file('main.py')
        .add_repository('tests')
            .add_file('__init__.py')
            .add_file('test_main.py')
    )
    return repo

if __name__ == '__main__':
    print(create_template('test'))
