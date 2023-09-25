import os
from flask import Flask, request, jsonify
from parser_module import TimingParser
import pymongo

app = Flask(__name__)

client = pymongo.MongoClient("mongodb+srv://vijaykumarp2f:PvPhnDdpokSjlO3S@cluster0.e1icshx.mongodb.net/")
db = client["DashBoard_Data"]
collection = db["Timing_data"]

class DataExtractor:
    def __init__(self, input_file):
        self.input_file = input_file
        self.primary_data = []

    def extract_data(self):
        with open(self.input_file, 'r') as file:
            lines = file.readlines()
            for line in lines[1:]:
                line = line.strip()
                if line:
                    parts = line.split(': ')
                    # print(parts)
                    if len(parts) == 3:
                        name, lead, directory = map(str.strip, parts)
                        self.primary_data.append({"name": name, "lead": lead, "directory": directory})
                        # print(self.primary_data)

    def get_data(self):
        return self.primary_data

def process_directories(input_file):
    try:
        data_extractor = DataExtractor(input_file)
        data_extractor.extract_data()
        data_entries = data_extractor.get_data()
        processed_files = set()

        for sl_no, entry in enumerate(data_entries, start=1):
            name = entry['name']
            directory = entry["directory"]
            lead = entry["lead"]

            # Initialize variables with default values
            spv_intra_slack, spv_inter_slack, pba_intra_slack, pba_inter_slack = None, None, None, None

            if os.path.exists(directory) and os.path.isdir(directory):
                print("Processing directory for '%s':'%s'" % (name, directory))

                subdirectory = os.path.join(directory, 'postroute')
                if os.path.exists(subdirectory) and os.path.isdir(subdirectory):
                    print("Subdirectory 'postroute' exists for '%s'" % directory)

                    # Print files inside 'postroute' subdirectory
                    subdirectory_files = os.listdir(subdirectory)
                    if subdirectory_files:
                        print("Files inside 'postroute' subdirectory for '%s':" % name)
                        for file_name in subdirectory_files:
                            print("- %s" % file_name)

                            # Check if the file has already been processed
                            if file_name in processed_files:
                                print("File '%s' already processed. Skipping." % file_name)
                                continue

                            file_path = os.path.join(subdirectory, file_name)
                            parser = TimingParser(file_path)
                            parsed_slack_values = parser.parse_files()

                            # Update slack_values based on file type
                            if 'SPV' in file_name:
                                spv_intra_slack = parsed_slack_values["spv_intra_slack"]
                                spv_inter_slack = parsed_slack_values["spv_inter_slack"]
                            elif 'PBA' in file_name:
                                pba_intra_slack = parsed_slack_values["pba_intra_slack"]
                                pba_inter_slack = parsed_slack_values["pba_inter_slack"]

                            # Append a dictionary with all values
                            results = {
                                "Sl.No": sl_no,
                                "Partition": name,
                                "Lead": lead,
                                "Intra_Voils(SPV)": spv_intra_slack,
                                "Intra_Voils(PBA)": spv_inter_slack,
                                "Inter_Voils(SPV)": pba_intra_slack,
                                "Inter_Voils(PBA)": pba_inter_slack,
                                "Util%": "Null",
                                "Congestion": "Null",
                                "Shorts": "Null",
                                "ETA": "",
                                "Comments": "",
                                "Plan of Action": "",
                                "Directory": directory,
                                "pre-info": [
                                    {
                                        "dateTime": " ",
                                        "comment": " ",
                                        },
                                    ]
                            }
                            # print(results)

                            # Add the processed file to the set
                            processed_files.add(file_name)

                            # Check if a similar document already exists in the collection
                            existing_document = collection.find_one({"Partition": name, "Directory": directory})
                            if existing_document is None:
                                result = collection.insert_one(results)
                                if result.acknowledged:
                                    print("Document for '%s' in '%s' inserted" % (name, directory))
                                else:
                                    print("Failed to insert document for '%s' in '%s'" % (name, directory))
                            else:
                                # Replace the existing document with the new one
                                result = collection.replace_one(
                                    {"Partition": name, "Directory": directory},
                                    results
                                )
                                if result.modified_count > 0:
                                    print("Document for '%s' in '%s' replaced" % (name, directory))
                                else:
                                    print("Failed to replace document for '%s' in '%s'" % (name, directory))

                    else:
                        print("No files found inside 'postroute' subdirectory for '%s'" % name)
                else:
                    print("Subdirectory 'postroute' does not exist for '%s'" % name)
            else:
                print("Directory does not exist")

        # Close the MongoDB client after all processing is done
        client.close()

        return {"message": "Directories processed successfully"}, 200

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/process_directories', methods=['GET','POST'])
def process_directories_route():
    input_file = "C:/Users/7396/Documents/BackendServer/partition.txt"
    result, status_code = process_directories(input_file)
    return jsonify(result), status_code

@app.route('/get_data', methods=['GET'])
def get_data():
    try:
        # Query the MongoDB collection to retrieve data
        data = list(collection.find())

        # Convert the MongoDB documents to a list of dictionaries
        data_list = []
        for doc in data:
            data_list.append({
                "Sl.No": doc["Sl.No"],
                "Partition": doc["Partition"],
                "Lead": doc["Lead"],
                "Intra_Voils(SPV)": doc["Intra_Voils(SPV)"],
                "Intra_Voils(PBA)": doc["Intra_Voils(PBA)"],
                "Inter_Voils(SPV)": doc["Inter_Voils(SPV)"],
                "Inter_Voils(PBA)": doc["Inter_Voils(PBA)"],
                "Util%": doc["Util%"],
                "Congestion": doc["Congestion"],
                "Shorts": doc["Shorts"],
                "ETA": doc["ETA"],
                "Comments": doc["Comments"],
                "Plan of Action": doc["Plan of Action"],
                "Directory": doc["Directory"],
                "pre-info": doc["pre-info"]
            })

        return jsonify(data_list), 200
    except Exception as e:
        return {"error": str(e)}, 500
    
    
if __name__ == '__main__':
    app.run(debug=True)
