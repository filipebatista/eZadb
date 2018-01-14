import os

import configparser as ConfigParser


class Config:
    class Section(object):
        def __init__(self, section_name, config):
            self.__section_name = section_name
            self.__configParser = config

        def __str__(self):
            return '%s: %s' % (self.__section_name, self.__configParser)

        def get(self, name):
            try:
                return self.__configParser.get(self.__section_name, name)
            except Exception as n_exp:
                print('Cannot found value for %s in config: %s\n' % (name, n_exp))
                return None

        def set(self, key, value):
            try:
                if not self.__configParser.has_section(self.__section_name):
                    self.__configParser.add_section(self.__section_name)
                self.__configParser.set(self.__section_name, key, str(value))
            except Exception as n_exp:
                print('Cannot set value %s for %s to config: %s\n' % (value, key, n_exp))

    def __init__(self, config_file_path):
        self.__confFilePath = config_file_path
        self.__sections = dict()
        self.__configParser = ConfigParser.ConfigParser()
        self.__configParser.optionxform = str
        self._add_config_ini(config_file_path)

    def get_section(self, name):
        if name not in self.__sections:
            self.__sections[name] = self.Section(name, self.__configParser)
        return self.__sections[name]

    def save_changes(self):
        with open(self.__confFilePath, 'w') as configfile:
            self.__configParser.write(configfile)

    def _add_config_ini(self, config_file_path):
        # check if the file exists
        if not os.path.exists(config_file_path):
            self.__configParser.write(open(config_file_path, 'w'))
        else:
            self.__configParser.read(config_file_path)
        self.__sections = dict(
            map(lambda section: (section, self.Section(section, self.__configParser)), self.__configParser.sections()))
