#!/usr/bin/env python
#
# Copyright 2014 Yoann Gini
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import random
import string

from autopkglib import Processor, ProcessorError

__all__ = ["PostgreSQL"]


class PostgreSQL(Processor):
    description = ("This process is an advanced process used to prepare a PostgreSQL database for new services."
                   ""
                   "Please, read the documentation carefuly before using it."
                   ""
                   "The process use the postgre_sql_host (and postgre_sql_port) server to work, if not set, the process will try to find the default local one."
                   "If you're on recent OS X Server, you can use postgre_sql_start_os_x_server_service to start the builtin PostgreSQL Server."
                   ""
                   "The process will use the postgre_sql_admin_name and postgre_sql_admin_password credentials if provided,"
                   "if not, it will try to act as the current user. You can force a sudo to a custom unix user with postgre_sql_sudo_account."
                   ""
                   "The process use postgre_sql_database inputs to determine the target base and postgre_sql_role_name for the owner."
                   ""
                   "If postgre_sql_drop_db_if_exist is true (not by default), the process will drop all existing information for a fresh start."
                   ""
                   "If the role don't exist, postgre_sql_role_name will be used to create a new one"
                   "with a random password available in output as postgre_sql_ouput_password, unless if postgre_sql_role_password is provided as input."
                   "If postgre_sql_always_replace_role_password is true and the user already exist, the process will reset the password."
                   "In any case, the role password is always available in postgre_sql_ouput_password."
                   ""
                   "If the database already exist and not droped by the process, the postgre_sql_update_input file is used if exist as an update procedure."
                   "Otherwise, if the database has beem created during the process, postgre_sql_creation_input file is used as SQL input file for new database."
                   ""
                   "Ut's possible to set postgre_sql_psql_path if you need to specify a custom psql path.")
    input_variables = {
        "postgre_sql_host": {
            "required": False,
            "description": ("The PostgreSQL server to use. It can be a host address or a local socket directory (the host parameter keyword from libpq)."),
        },
        "postgre_sql_port": {
            "required": False,
            "description": ("The PostgreSQL port to use if the postgre_sql_host is a host address (the port parameter keyword from libpq)."),
        },
        "postgre_sql_admin_name": {
            "required": False,
            "description": ("The PostgreSQL admin account to use."),
        },
        "postgre_sql_admin_password": {
            "required": False,
            "description": ("The PostgreSQL admin password to use."),
        },
        "postgre_sql_database": {
            "required": True,
            "description": ("The PostgreSQL database to create or use."),
        },
        "postgre_sql_role_name": {
            "required": False,
            "description": ("The PostgreSQL username to create."),
        },
        "postgre_sql_role_password": {
            "required": False,
            "description": ("Specify a default password to use. If not provided, a random one will be generated and set."),
        },
        "postgre_sql_always_replace_role_password": {
            "required": False,
            "description": ("If true and if postgre_sql_role_name already exist, the password will be updated with regular rules for postgre_sql_role_password."),
        },
        "postgre_sql_start_os_x_server_service": {
            "required": False,
            "description": ("Start the OS X Server PostgreSQL service if needed. True by default, will fail the process if the service can't be started."),
        },
        "postgre_sql_drop_db_if_exist": {
            "required": False,
            "description": ("If the target base already exist, the process will drop it and start from fresh one. (False by default)"),
        },
        "postgre_sql_update_input": {
            "required": False,
            "description": ("PostgreSQL command file to use against the target database if the database already exist."),
        },
        "postgre_sql_creation_input": {
            "required": False,
            "description": ("PostgreSQL command file to use against the target database if the database don't exist."),
        },
        "postgre_sql_psql_path": {
            "required": False,
            "description": ("PostgreSQL psql binary path, default value is just 'psql'."),
        },
        "postgre_sql_sudo_account": {
            "required": False,
            "description": ("Execute all psql command from this unix user account via sudo."),
        },
        "postgre_sql_initial_connexion_database": {
            "required": False,
            "description": ("Default database for the connexion to the server. Default is template1."),
        },
    }
    output_variables = {
        "postgre_sql_ouput_password": {
            "description": ("The PostgreSQL password to use with the database. It can be a generated one or the postgre_sql_role_password set in input."),
        },
    }
    
    __doc__ = description
    
    psql_base_command = []
    postgre_sql_initial_connexion_database = None
    
    
    def run_psql_command(self, command, dbname=None):
        if not dbname:
            dbname = self.postgre_sql_initial_connexion_database
        return self.run_psql_with_args(['-d', dbname, '-tAc', command])
    
    
    def run_psql_with_args(self, commands_array):
        final_commands = self.psql_base_command[:]
        final_commands.extend(commands_array)
        command_result = subprocess.check_output(final_commands)
        return command_result
    
    
    def check_db_service_or_die(self):
        self.output("Check if we are able to connect to the PostgreSQL Server.")
        try:
            self.run_psql_command(';')
            self.output("Connexion OK.")
        except Exception:
            raise ProcessorError("Impossible to connect to database server")
        
        
    def check_db_existance(self, dbname):
        self.output("Check if %s database already exist." % dbname)
        result = self.run_psql_command("SELECT 1 FROM pg_database WHERE datname='%s'" % dbname)
        if result:
            self.output("Database exist.")
            return True
        else:
            self.output("Database don't exist.")
            return False 
    
    
    def drop_database(self, dbname):
        self.output("Drop pre existing database %s" % dbname)
        self.run_psql_command("DROP DATABASE %s" % dbname)
    
    
    def create_database(self, dbname, owner):
        self.output("Create database %s" % dbname)
        self.run_psql_command("CREATE DATABASE %s OWNER %s" % (dbname, owner))
        
        
    def check_role_existance(self, role):
        self.output("Check if %s role already exist." % role)
        result = self.run_psql_command("SELECT 1 FROM pg_roles WHERE rolname='%s'" % role)
        if result:
            self.output("Role exist.")
            return True
        else:
            self.output("Role don't exist.")
            return False 
    
    
    def create_role_with_password(self, role, password):
        self.output("Create role %s" % role)
        self.run_psql_command("CREATE ROLE %s WITH PASSWORD '%s'" % (role, password))
    
    
    def update_role_with_password(self, role, password):
        self.output("Update role %s" % role)
        self.run_psql_command("ALTER ROLE %s WITH PASSWORD '%s'" % (role, password))
    
    
    def execute_sql_file_to_db(self, sql_file, dbname):
        self.output("Load SQL file %s into %s" % (sql_file, dbname))
        self.run_psql_with_args(['-d', dbname, '-f', sql_file])
    
    
    def main(self):
        postgre_sql_host = self.env.get('postgre_sql_host', None)
        postgre_sql_port = self.env.get('postgre_sql_port', None)
        
        postgre_sql_admin_name = self.env.get('postgre_sql_admin_name', None)
        postgre_sql_admin_password = self.env.get('postgre_sql_admin_password', None)
        
        postgre_sql_database = self.env['postgre_sql_database']
        postgre_sql_role_name = self.env['postgre_sql_role_name']
        postgre_sql_role_password = self.env.get('postgre_sql_role_password', ''.join(random.choice(string.hexdigits) for i in range(12)))
        postgre_sql_always_replace_role_password = self.env.get('postgre_sql_always_replace_role_password', False)
        
        postgre_sql_start_os_x_server_service = self.env.get('postgre_sql_start_os_x_server_service', True)
        
        postgre_sql_drop_db_if_exist = self.env.get('postgre_sql_drop_db_if_exist', False)
        
        postgre_sql_update_input = self.env.get('postgre_sql_update_input', None)
        postgre_sql_creation_input = self.env.get('postgre_sql_creation_input', None)
        
        postgre_sql_psql_path = self.env.get('postgre_sql_psql_path', "psql")
        postgre_sql_sudo_account = self.env.get('postgre_sql_sudo_account', None)
        
        self.postgre_sql_initial_connexion_database = self.env.get('postgre_sql_initial_connexion_database', 'template1')
        
        db_created_on_this_run = False
        
        ### Create the baseline for psql command line which will be used to run all SQL commands
        if postgre_sql_sudo_account:
            self.psql_base_command.append('sudo')
            self.psql_base_command.append('-u')
            self.psql_base_command.append(postgre_sql_sudo_account)
        
        self.psql_base_command.append(postgre_sql_psql_path)
        
        # Construct the connection keys string from available input. The final format look like "user=alice password=NotBobAgain host=203.0.113.42 port=1234"
        user_name_with_key = ""
        password_with_key = ""
        port_with_key = ""
        host_with_key = ""
        if postgre_sql_admin_name:
            user_name_with_key = "user=%s" % postgre_sql_admin_name
            if postgre_sql_admin_password:
                password_with_key = "password=%s" % postgre_sql_admin_password
        if postgre_sql_host:
            host_with_key = "host=%s" % postgre_sql_host
        if postgre_sql_port:
            port_with_key = "port=%s" % postgre_sql_port
        connkeys = '%s %s %s %s' % (user_name_with_key, password_with_key, host_with_key, port_with_key)  
        if not connkeys.isspace():
            self.psql_base_command.append(connkeys)
        
        ### Start PostgreSQL on OS X Server if needed
        if postgre_sql_start_os_x_server_service:
            self.output("Start OS X Server PostgreSQL server if needed.")
            postgre_sql_state = subprocess.check_output(["serveradmin", "start", "postgres"])
            print postgre_sql_state
                
        ### Service check
        self.check_db_service_or_die()
        
        ### State discovery and adjustments            
        role_exist = self.check_role_existance(postgre_sql_role_name)
        if role_exist and postgre_sql_always_replace_role_password:
            self.update_role_with_password(postgre_sql_role_name, postgre_sql_role_password)
        elif not role_exist:
            self.create_role_with_password(postgre_sql_role_name, postgre_sql_role_password)
            role_exist = True
        
        db_exist = self.check_db_existance(postgre_sql_database)
        if db_exist and postgre_sql_drop_db_if_exist:
            self.drop_database(postgre_sql_database)
            db_exist = False
            
        if not db_exist:
            self.create_database(postgre_sql_database, postgre_sql_role_name)
            db_exist = True
            db_created_on_this_run = True
        
        ### SQL loading
        if db_created_on_this_run and postgre_sql_creation_input:
            self.execute_sql_file_to_db(postgre_sql_creation_input, postgre_sql_database)
        elif not db_created_on_this_run and postgre_sql_update_input:
            self.execute_sql_file_to_db(postgre_sql_update_input, postgre_sql_database)
        
        ### End
        self.env['postgre_sql_ouput_password'] = postgre_sql_role_password

if __name__ == '__main__':
    processor = PostgreSQL()
    processor.execute_shell()
    
