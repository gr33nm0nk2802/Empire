from __future__ import print_function

from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        username = params['Username']
        password = params['Password']
        instance = params['Instance']
        check_all = params['CheckAll']

        # read in the common module source code
        sql_info_source = main_menu.installPath + "/data/module_source/situational_awareness/network/Get-SQLServerInfo.ps1"
        script = ""
        if obfuscate:
            data_util.obfuscate_module(moduleSource=sql_info_source, obfuscationCommand=obfuscation_command)
            sql_info_source = sql_info_source.replace("module_source", "obfuscated_module_source")
        try:
            with open(sql_info_source, 'r') as source:
                script = source.read()
        except:
            return handle_error_message("[!] Could not read module source path at: " + str(sql_info_source))

        script_end = ""
        if check_all:
            sql_instance_source = main_menu.installPath + "data/module_source/situational_awareness/network/Get-SQLInstanceDomain.ps1"
            if obfuscate:
                data_util.obfuscate_module(moduleSource=sql_info_source, obfuscationCommand=obfuscation_command)
                sql_instance_source = sql_info_source.replace("module_source", "obfuscated_module_source")
            try:
                with open(sql_instance_source, 'r') as auxSource:
                    auxScript = auxSource.read()
                    script += " " + auxScript
            except:
                print(helpers.color("[!] Could not read additional module source path at: " + str(sql_instance_source)))
            script_end = " Get-SQLInstanceDomain "
            if username != "":
                script_end += " -Username "+username
            if password != "":
                script_end += " -Password "+password
            script_end += " | "

        script_end += " Get-SQLServerInfo"
        if username != "":
            script_end += " -Username "+username
        if password != "":
            script_end += " -Password "+password
        if instance != "" and not check_all:
            script_end += " -Instance "+instance

        outputf = params.get("OutputFunction", "Out-String")
        script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = data_util.keyword_obfuscation(script)

        return script

