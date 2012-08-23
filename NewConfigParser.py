#############################################################################################
#
# NewConfigParser.py
#
# Written by Shreyas Kulkarni, released on 23-Aug-2012
#
# Copyright (c) 2012, Shreyas Kulkarni (shyran _at_ gmail _dot_ com)
# All rights reserved.
#
# The NewConfigParser extension is licensed under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance with the License.
# You may obtain a copy of the License at - http://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
#
#############################################################################################

import re
import ConfigParser

class CircularDependancyException(Exception):
    def __init__(self, param, dependancylist):
        self.faulty_param = param
        self.dependancy_list = dependancylist

        #append the faulty param to make the cicular dependancy clearer
        self.dependancy_list.append(self.faulty_param)

    def __str__(self):
        return("Cicrular dependancy detected while resolving parameter '" + 
               self.faulty_param + "': " + 
               " -> ".join(self.dependancy_list[self.dependancy_list.index(self.faulty_param):]))



class SafeConfigParser(ConfigParser.SafeConfigParser):
    def __init__(self, defaults=None):
        #SafeConfigParser is old-style class, so super wont work
        ConfigParser.SafeConfigParser.__init__(self, defaults)

        #substitution pattern in the config file: ${section.parameter}
        self.subs_pattern = "\$\{[^\$\{\}]*\}"
        
        #local cache for the configuration parameters
        self.config_params_cache = {}

        #mechanism to detect circular dependancies
        self.dependancy_list = []

        
    def get(self, section, parameter, raw=False, vars=None):
        #get a reference to original get method
        superget = ConfigParser.SafeConfigParser.get

        uniq_param_id = section + "." + parameter

        #first, check if the parameter is available in the local cache
        if (uniq_param_id in self.config_params_cache):
            return self.config_params_cache[uniq_param_id]

        try:
            raw_val = superget(self, section, parameter, raw, vars)
        except Exception as err:
            #substitute with a blank if the replacement value is not found in the config file
            raw_val = ""

        #if there are no placeholders in the value, just return it as it is
        if not re.search(self.subs_pattern, raw_val):
            self.config_params_cache[uniq_param_id] = raw_val
            return raw_val
        
        #add the parameter to the dependancy_list so that any circular dependancies later, can be detected
        self.dependancy_list.append(uniq_param_id)

        #raw replace the found entries
        while re.search(self.subs_pattern, raw_val):
            match = [x for x in re.finditer(self.subs_pattern, raw_val)][0]
            placeholder = raw_val[match.start() + 2 : match.end() - 1]

            #if '.' is not found in the name, assume the parameter is from the same section as this
            subs_section = section
            subs_param = placeholder
            if '.' in placeholder:
                sep_idx = placeholder.index('.')
                subs_section = placeholder[0 : sep_idx]
                subs_param = placeholder[sep_idx + 1 : ]
            
            #if the parameter is already in the dependancy list, raise a circular dependancy exception
            uniq_subsparam_id = subs_section + "." + subs_param
            if (uniq_subsparam_id not in self.dependancy_list):
                replacement = self.get(subs_section, subs_param, raw, vars)
            else:
                raise CircularDependancyException(uniq_subsparam_id, self.dependancy_list)

            raw_val = raw_val[:match.start()] + replacement + raw_val[match.end():]

        #cache the parameter access
        self.config_params_cache[uniq_param_id] = raw_val

        #remove the dependancy
        self.dependancy_list.remove(uniq_param_id)

        return raw_val

