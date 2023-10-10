import os
import re


class SPV:
    def __init__(self):
        self.pattern = {
            "intra": re.compile(r"(\s+Path Group: reg_to_reg(.*?)slack\s+\((VIOLATED|MET)\)\s+(-?\d+\.\d+))", re.DOTALL),
            "inter": re.compile(r"(\s+Path Group: (input_to_reg|reg_to_output)(.*?)slack\s+\((VIOLATED|MET)\)\s+(-?\d+\.\d+))", re.DOTALL),
            "slack_pattern": re.compile(r"\s+slack \(VIOLATED\)\s+(-?\d+\.\d+)")
        }
    def parse_file(self,file_content):
        intra_slack_values =[]
        inter_slack_values =[]
        intra_path = self.pattern['intra'].findall(file_content)
        for idx, path_match in enumerate(intra_path):
            slack_match = self.pattern['slack_pattern'].search(path_match[0])
            intra_slack_values.append(float(slack_match.group(1)))
        intra_wns = min(intra_slack_values)
        intra_tns = sum(intra_slack_values)
        intra_fep = len(intra_slack_values)
        intra_slack = {"wns":intra_wns,
                       "tns":intra_tns,
                       "fep":intra_fep}
                    
        # print(intra_slack_values)
        inter_path = self.pattern['inter'].findall(file_content)
        for idx, path_match in enumerate(inter_path):
            slack_match = self.pattern['slack_pattern'].search(path_match[0])
            inter_slack_values.append(float(slack_match.group(1)))
        # Calculate WNS, TNS, and FEP for inter
        inter_wns = min(inter_slack_values)
        inter_tns = sum(inter_slack_values)
        inter_fep = len(inter_slack_values)
        inter_slack = {"wns":inter_wns,
                       "tns":inter_tns,
                       "fep":inter_fep}
        
        return intra_slack, inter_slack
    
class PBA:
    def __init__(self):
        self.pattern = {
            "intra": re.compile(r"(\s+Path Group: reg_to_reg(.*?)slack\s+\((VIOLATED|MET)\)\s+(-?\d+\.\d+))", re.DOTALL),
            "inter": re.compile(r"(\s+Path Group: (input_to_reg|reg_to_output)(.*?)slack\s+\((VIOLATED|MET)\)\s+(-?\d+\.\d+))", re.DOTALL),
            "slack_pattern": re.compile(r"\s+slack \(VIOLATED\)\s+(-?\d+\.\d+)")
        }
    def parse_file(self,file_content):
        intra_slack_values =[]
        inter_slack_values =[]
        intra_path = self.pattern['intra'].findall(file_content)
        for idx, path_match in enumerate(intra_path):
            slack_match = self.pattern['slack_pattern'].search(path_match[0])
            intra_slack_values.append(float(slack_match.group(1)))
        intra_wns = min(intra_slack_values)
        intra_tns = sum(intra_slack_values)
        intra_fep = len(intra_slack_values)
        intra_slack = {"wns":intra_wns,
                       "tns":intra_tns,
                       "fep":intra_fep}
                    
        # print(intra_slack_values)
        inter_path = self.pattern['inter'].findall(file_content)
        for idx, path_match in enumerate(inter_path):
            slack_match = self.pattern['slack_pattern'].search(path_match[0])
            inter_slack_values.append(float(slack_match.group(1)))
        # Calculate WNS, TNS, and FEP for inter
        inter_wns = min(inter_slack_values)
        inter_tns = sum(inter_slack_values)
        inter_fep = len(inter_slack_values)
        inter_slack = {"wns":inter_wns,
                       "tns":inter_tns,
                       "fep":inter_fep}
        
        return intra_slack, inter_slack
    
class TimingParser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pattern = {
            "PBApattern": re.compile(r'^[a-zA-Z0-9_-]*(timing|TIMING)[a-zA-Z0-9_-]*PBA\.(rpt|txt)$'),
            "SPVpattern": re.compile(r'^[a-zA-Z0-9_-]*(timing|TIMING)[a-zA-Z0-9_-]*SPV\.(rpt|txt)$'),
        }
        self.summary = {}

    def parse_files(self):
        spv_intra_slack, spv_inter_slack = None, None
        pba_intra_slack, pba_inter_slack = None, None
        try:
            if self.file_path:
                print(self.file_path)
                if self.pattern['SPVpattern'].match(os.path.basename(self.file_path)):
                    parser = SPV()
                    with open(self.file_path, 'r') as file:
                        file_content = file.read()
                    spv_intra_slack,spv_inter_slack = parser.parse_file(file_content)
                    
                elif self.pattern['PBApattern'].match(os.path.basename(self.file_path)):
                    parser = PBA()
                    with open(self.file_path, 'r') as file:
                        file_content = file.read()
                    pba_intra_slack,pba_inter_slack = parser.parse_file(file_content)
                else:
                    print("not SPV nor PBA")
                return {
                    "spv_intra_slack": spv_intra_slack,
                    "spv_inter_slack": spv_inter_slack,
                    "pba_intra_slack": pba_intra_slack,
                    "pba_inter_slack": pba_inter_slack
                }
                    
                
        except Exception as e:
            print("Error:", e)


class UtilizationParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_files(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if "utilization %" in line.lower():
                        utilization_percentage = line.split(":")[-1].strip()
                        # print(utilization_percentage)
                        # print('***************************&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&****************************************')
                        return utilization_percentage
            return None  # Return None if utilization data is not found
        except Exception as e:
            print(f"Error parsing utilization report: {str(e)}")
            return None
        

class ShortsParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_files(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    print(lines)
                    if "shorts :" in line.lower():
                        shorts = line.split(":")[-1].strip()
                        # print(shorts)
                        return shorts
            return None  # Return None if shorts data is not found
        except Exception as e:
            print(f"Error parsing shorts report: {str(e)}")
            return None


class CongestionParser:
    def __init__(self, file_path):
        self.file_path = file_path

    def parse_files(self):
        try:
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines:
                    if "congestion :" in line.lower():
                        congestion = line.split(":")[-1].strip()
                        return congestion
            return None  # Return None if congestion data is not found
        except Exception as e:
            print(f"Error parsing congestion report: {str(e)}")
            return None
