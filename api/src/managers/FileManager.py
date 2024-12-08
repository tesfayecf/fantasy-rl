import json, os, re, time, hashlib

from api.common.utils.DictStack import DictStack
from .RequestManager import RequestManager

class FileManager:
    """
    The `FileManager` class provides a set of methods for reading, saving, and updating files, with a focus on JSON files.
    It allows customization of the file reading and writing functions and provides the ability to read, save, and update JSON data.

    Attributes:
    - `requestManager`: An instance of the `RequestManager` class used for making requests.

    Methods:
    - `read(file_path: str, format: str = "json") -> Any`: Reads and returns the content of a file, with support for different formats.
    - `write(file_path: str, data: Any, meta: dict, format: str = "json")`: Saves data to a file, overwriting the file content or creating a new file.
    
    Private Methods:
    - `__update_data(meta: dict) -> Tuple[dict, Any]`: Updates the file data from a specified URL and returns the updated data and metadata.
    - `__check_path_recursive(path: str, format: str = "json")`: Recursively checks and creates directories for the given file path.
    """

    cache = DictStack(150)

    requestManager: RequestManager = None

    def __init__(self, requestManager: RequestManager):
        self.requestManager = requestManager

    def setConfig():
        pass

    def read(self, file_path, base_meta, format="json"):
        """
        Reads and returns the content of a file, with support for different formats.

        Args:
            file_path (str): The path to the file to read.
             meta (dict): Metadata associated with the file.
            format (str, optional): The format of the file (default is "json").

        Returns:
            Any: The content of the file.
        """

        # Check if the parent directory exists and create it if necessary
        # TODO: need to provide meta to the params to know where to fetch in the first read
        # Should make a write with correct meta and dammy data and then read to update it
        # This can be done in the same class or by the services themselves
        
        # ALERT: this meta is only used for the first write/read
        self.__check_path_recursive(file_path, base_meta)
        hashed_file_path = self.hash_file_path(file_path)
        try:
            if format == "json":
                meta = None
                data = None
                
                cached = self.cache.get(hashed_file_path)
                if cached:
                    data = cached['data']
                    meta = cached['meta']
                else:
                    with open(file_path, 'a+') as file:
                        file.seek(0)
                        
                        try:
                            file_content = json.load(file)
                        except json.decoder.JSONDecodeError:
                            raise Exception("Invalid JSON file")

                        if "meta" not in file_content:
                            raise Exception("'meta' not found")
                        if "data" not in file_content:
                            raise Exception("'data' not found")

                        meta = file_content["meta"]
                        data = file_content["data"]

                required_metadata_fields = ["id", "name", "url", "last_update", "update_interval", "fields"]
                missing_fields = [field for field in required_metadata_fields if field not in meta]
                if missing_fields:
                    raise Exception(f"Missing required metadata fields: {', '.join(missing_fields)}")

                id = meta["id"]
                current_time = int(time.time())
                last_update = meta["last_update"]
                update_interval = meta["update_interval"]

                if current_time - last_update >= update_interval:
                    new_data, new_meta = self.__update_data(data, meta)
                    if new_data is not None and new_meta is not None:
                        # Update the file and cache with the updated data and metadata
                        succes = self.write(new_data, file_path, new_meta, format="json")
                        if not succes:
                            raise Exception(f"Error writing updated file with id {id}")
                        self.cache.push(hashed_file_path, {"data": new_data, "meta": new_meta})
                        return new_data
                    else:
                        raise Exception(f"Error updating file with id {id}")
                if data is not None and meta is not None:
                    return data
                else: 
                    raise Exception(f"Error reading file with id {id}")
            else:
                with open(file_path, 'r') as file:
                    return file.read()
        except Exception as e:
            print(f'FileManager::Read: {str(e)}')
            return None

    def write(self, data, file_path, meta, format="json"):
        """
        Saves data to a file, overwriting the file content or creating a new file.

        Args:
            data (Any): The data to be saved.
            file_path (str): The path to the file.
            meta (dict): Metadata associated with the data.
            format (str, optional): The format of the file (default is "json").
        """
        # Check if the parent directory exists and create it if necessary
        self.__check_path_recursive(file_path, meta)

        # Ensure that required metadata fields are provided
        required_fields = ["id", "name", "url", "last_update", "update_interval", "fields"]
        if not all(field in meta for field in required_fields):
            raise Exception("Missing required metadata fields")

        try:
            if format == "json":
                if isinstance(data, dict):
                    # Update the existing data with the new data
                    # data = {field: data[field] for field in meta["fields"]}
                    # ALERT: params are checked by caller function
                    new_data = {"meta": meta, "data": data}

                    # Write the updated JSON data to the file
                    with open(file_path, 'w+') as file:
                        json.dump(new_data, file, indent=4)
                    return True
                elif isinstance(data, list):
                    new = []
                    for item in data:
                        if isinstance(item, dict):
                            new.append(item)
                        else:
                            raise Exception("Cannot update JSON data with non-dictionary items")
                    new_data = {"meta": meta, "data": new}

                    # Write the updated JSON data to the file
                    with open(file_path, 'w+') as file:
                        json.dump(new_data, file, indent=4)
                    return True
                else:
                    raise Exception("Cannot update JSON data with invalid format")
            else:
                with open(file_path, 'w+') as file:
                    file.write(data)
                return True
        except Exception as e:
            print(f'FileManager::write : {str(e)}')
            return False        
    
    #######################
    ### PRIVATE METHODS ###
    #######################

    def __update_data(self, data, meta):
        try:
            if not re.search(r'^https?://', meta["url"]) and not re.search(r'^http?://', meta["url"]):
                raise Exception("Invalid URL")
            
            new_data = self.requestManager.get(meta["url"], timeout=5)
            new_data = new_data.result()
            new_data = json.loads(new_data.text)

            # Update data
            if isinstance(new_data, dict):
                data = {field: new_data[field] for field in meta["fields"]}
            elif isinstance(new_data, list):
                data = []
                for item in new_data:
                    if isinstance(item, dict):
                        new_d = {field: item.get(field, None) for field in meta["fields"]}
                        data.append(new_d)
                    else:
                        raise Exception("Cannot update JSON data with non-dictionary items")
            else:
                raise Exception("New data is not a dictionary nor a list")
                
            # Update metada 
            meta["last_update"] = int(time.time())

            return data, meta
        except Exception as e:
            print(f'FileManager::__update_data: {str(e)}')
            return None, None

    def __check_path_recursive(self, path, meta=None, format="json"):
        if not os.path.exists(path):
            parent_directory = os.path.dirname(path)
            self.__check_path_recursive(parent_directory)
            isfile = re.search(r'\.[A-Za-z0-9]+$', path)
            if not isfile:
                os.makedirs(path + '/', mode=0o777, exist_ok=True)
            elif isfile:
                if format == "json":
                    with open(path, 'x') as file:
                        if meta:
                            default = { "meta": meta, "data": {}}
                        else:
                            raise Exception("Missing required metadata fields")
                        json.dump(default, file, indent=4)
                else:
                    with open(path, 'x') as file:
                        pass
        else:
            return
    
    def hash_file_path(self, file_path):
        sha256 = hashlib.sha256()
        sha256.update(file_path.encode('utf-8'))
        return sha256.hexdigest()