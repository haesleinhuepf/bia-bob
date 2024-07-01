class HintVectorStore():
    def __init__(self):
        import os
        import importlib_metadata
        from importlib.metadata import entry_points
        import pandas as pd
        import yaml
        
        # load cache from disk if it exists
        home_dir = os.path.expanduser('~')
        store_filename = os.path.join(home_dir, ".cache", "bia-bob", "bia_bob_vectore_store.yaml")
        os.makedirs(os.path.dirname(store_filename), exist_ok=True)
        if os.path.exists(store_filename):
            #df_dict = pd.read_csv(store_filename)
            with open(store_filename, mode="rt", encoding="utf-8") as test_df_to_yaml:
                df_dict = pd.DataFrame(yaml.full_load(test_df_to_yaml)['vectorstore'])
            db_dict = df_dict.to_dict(orient="list")
        else:
            # create empty cache
            db_dict = {
                "package":[],
                "hint":[],
                "vector":[],
            }
            df_dict = pd.DataFrame(db_dict)

        # scan installed modules that are compatible plugins for hints   
        try:
            bia_bob_plugins = entry_points(group='bia_bob_plugins')
        except TypeError:
            all_plugins = entry_points()
            try:
                bia_bob_plugins = all_plugins['bia_bob_plugins']
            except KeyError:
                bia_bob_plugins = []
        
        all_modules = importlib_metadata.packages_distributions()
        for b in bia_bob_plugins:
            module_name = b.value.split(".")[0]
            package_name = all_modules[module_name][0]
            package_version = get_package_version(package_name)

            package_name_and_version = package_name + "==" + package_version

            # check if these functions are in the hint-vector store already. If not: add them
            if df_dict[df_dict["package"] == package_name_and_version].size == 0: 
                print("BiA-Bob is scanning and caching", package_name_and_version)
                func = b.load()
                hints = func()
                parse_hints_to_dict(hints, db_dict, package_name_and_version)

        # convert to DataFrame and save to disk
        df_dict = pd.DataFrame(db_dict)
        with open(store_filename, 'w') as file:
            documents = yaml.dump({'vectorstore': df_dict.to_dict(orient='records')}, file, default_flow_style=False)
        
        # get all packages+versions in cache
        unique_packages = df_dict['package'].unique().tolist()

        # check if they are installed 
        installed_packages = []
        for k, v in all_modules.items():
            for package_name in v:
                package_version = get_package_version(package_name)
                package_name_and_version = package_name+"=="+package_version
                if package_name_and_version in unique_packages or package_name in unique_packages:
                    installed_packages.append(package_name_and_version)

        # only keep cache for installed packages
        df_dict = df_dict[df_dict['package'].isin(installed_packages)]
        # keep a dictionary {vector:hint}
        self._vector_store = df_dict.set_index('vector')['hint'].to_dict()
    
    def search(self, text, n_best_results=3):
        import numpy as np
        single_vector = np.asarray(embed(text))
        
        # Step 1: inner products, vector
        inner_products = [(np.dot(single_vector, np.asarray(vector)), vector) for vector in self._vector_store.keys()]

        # Step 2: Sort inner products and get the three vectors with the maximum inner product
        inner_products.sort()
        inner_products.reverse()
        closest_vectors = [vec for _, vec in inner_products[:n_best_results]]  # Extract only the vectors
        
        # Step 1: Compute Euclidean distances
        #distances = [(np.linalg.norm(single_vector - np.asarray(vector)), vector) for vector in self._vector_store.keys()]

        # Step 2: Sort distances and get the three vectors with the shortest distances
        #distances.sort()  # Sort based on the first element in the tuple (distance)
        #closest_vectors = [vec for _, vec in distances[:n_best_results]]  # Extract only the vectors
        
        return [self._vector_store[tuple(v)] for v in closest_vectors]

def parse_hints_to_dict(hints, db_dict, package_name_and_version):
    instructions = hints
    while "\n " in instructions:
        instructions = instructions.replace("\n ", "\n")
    instructions = instructions.replace("\n    \n", "\n\n").strip().split("\n\n")

    for i in instructions:
        e = embed(i)

        db_dict["package"].append(package_name_and_version)
        db_dict["hint"].append(i)
        db_dict["vector"].append(tuple(e))

def embed(text):
    from openai import OpenAI
    client = OpenAI()
    #print("embedding", text)

    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small" # todo: make configurable
    )
    return response.data[0].embedding

def get_package_version(package_name):
    from importlib.metadata import version
    return version(package_name)
