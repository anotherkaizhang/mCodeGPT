import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
# import pygraphviz as pgv
import copy
import csv

import openai

class mCodeGPT:
    def __init__(self, df_ontology, df_prompt, df_promptYesNo, deployment_name, input_text, method):

        # Create a directed graph
        self.G = nx.DiGraph()
        self.df_ontology = df_ontology
        self.df_prompt = df_prompt
        self.df_promptYesNo = df_promptYesNo

        self.input_txt = input_text
        self.deployment_name = deployment_name
        self.method =  method

        # Initialize variables to keep track of the parent node at each level
        parents = {}

        # Iterate through the tree structure DataFrame and add nodes and edges to the graph
        for index, row in self.df_ontology.iterrows():
            for i, cell in enumerate(row):
                if pd.notna(cell):  # Skip NaN values
                    node_label = str(cell).strip('"')  # Remove double quotes if present
                    node_label = node_label.strip().lower().replace(' ', '_').replace('-', '_')
                    self.G.add_node(node_label, layer=i)  # Add the node
                    if i == 0:  # The root node
                        parents[i] = node_label
                    else:
                        parent = parents[i - 1]  # Get the parent node from the previous level
                        parents[i] = node_label  # Update the parent for the current level
                        self.G.add_edge(parent, node_label)  # Add an edge to the parent node

        # Iterate through the descriptions DataFrame and add descriptions as attributes
        for index, row in self.df_prompt.iterrows():
            for i, cell in enumerate(row):
                if pd.notna(cell):  # Skip NaN values
                    node_label = str(self.df_ontology.iat[index, i]).strip('"')  # Get the corresponding node label
                    node_label = node_label.strip().lower().replace(' ', '_').replace('-', '_')
                    description = str(cell).strip('"')  # Get the description
                    self.G.nodes[node_label]['description'] = description  # Add description as an attribute to the node
                    self.G.nodes[node_label][
                        'information_present_flag'] = 'YES'  # Add description as an attribute to the node

        # This is for method 3: only leaf node has attribute 'description(yesno)'
        for index, row in self.df_promptYesNo.iterrows():
            for i, cell in enumerate(row):
                if pd.notna(cell):  # Skip NaN values
                    node_label = str(self.df_ontology.iat[index, i]).strip('"')  # Get the corresponding node label
                    node_label = node_label.strip().lower().replace(' ', '_').replace('-', '_')
                    description = str(cell).strip('"')  # Get the description
                    self.G.nodes[node_label][
                        'description(yesno)'] = description  # Add description as an attribute to the node

        """
        G_update: the update of G with 'information_present_flag' changed based on previous layer
        cur_layer
        """
        # Determine the maximum layer in the graph
        self.max_layer = max([self.G.nodes[node].get('layer', 0) for node in self.G.nodes()])

        # Initialize a dictionary to group nodes by layer
        self.layer_nodes = {layer: [] for layer in range(self.max_layer + 1)}

        # Group nodes by layer
        for node in self.G.nodes():
            layer = self.G.nodes[node].get('layer', 0)
            self.layer_nodes[layer].append(node)
            self.G.nodes[node]['information_present_flag'] = 'YES'

    def plot_G(self, ):
        # You now have a NetworkX graph representing the tree structure with descriptions as attributes

        # # Create a Matplotlib figure and axis
        # fig, ax = plt.subplots()

        # # Position nodes using a spring layout
        # pos = nx.spring_layout(G)

        # # # Define labels for the nodes (with descriptions)
        # # labels = {node: f"{node}\n{G.nodes[node]['description']}" for node in G.nodes()}

        # # Define labels for the nodes
        # labels = {node: node for node in G.nodes()}

        # # Draw the graph on the axis
        # nx.draw(G, pos, with_labels=True, labels=labels, node_size=500, node_color='lightblue', font_size=10, font_color='black', ax=ax)

        # # Display the graph
        # plt.show()

        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots()

        # Use the NetworkX dot layout for a top-down tree structure
        pos = nx.nx_agraph.pygraphviz_layout(self.G, prog='dot')

        # Define labels for the nodes (with descriptions)
        # labels = {node: f"{node}\n{G.nodes[node]['description']}" for node in G.nodes()}

        # # Define labels for the nodes
        labels = {node: node for node in self.G.nodes()}

        # Draw the graph on the axis
        nx.draw(self.G, pos, with_labels=True, labels=labels, node_size=500,
                node_color='lightblue', font_size=10, font_color='black', ax=ax)

        # Display the graph
        plt.show()

    """============================# 1. Generate prompt======================================="""

    # Method 1: all leaf node
    def method1(self, ):

        # Find leaf nodes (nodes without children)
        leaf_nodes = [node for node in self.G.nodes() if self.G.out_degree(node) == 0]

        # Generate the text for leaf nodes with descriptions
        prompt = ["From the text below, extract the following entities in the following format: \n"]
        for node in leaf_nodes:
            description = self.G.nodes[node]['description']
            node = node.strip().lower().replace(' ', '_').replace('-', '_')
            prompt.append(f"{node}: <{description}>")

        # Create a text block with the descriptions for all leaf nodes
        prompt = "\n".join(prompt)
        #         print(prompt)
        return prompt

    def update_G(self, output_csv):
        self.G = copy.deepcopy(self.G)  # Create a deep copy of the original graph

        def update_flag_recursive(G, node):
            G.nodes[node]['information_present_flag'] = 'NO'
            for child in G.neighbors(node):
                update_flag_recursive(G, child)

        for _, row in output_csv.iterrows():
            node, answer = row
            if 'yes' in answer.lower():
                #             print('haha')
                self.G.nodes[node]['information_present_flag'] = 'YES'
            else:
                self.G.nodes[node]['information_present_flag'] = 'NO'
                update_flag_recursive(self.G, node)

    def method2(self, cur_layer):

        # Generate text for nodes by layer
        #     for layer, nodes in layer_nodes[cur_layer].items():
        layer = cur_layer
        nodes = self.layer_nodes[cur_layer]

        node_text = []

        for node in nodes:
            description = self.G.nodes[node]['description']
            information_present_flag = self.G.nodes[node]['information_present_flag']
            #         print(node, description, information_present_flag)
            if information_present_flag == 'YES' or information_present_flag == 'yes' or information_present_flag == 'Yes':
                node = node.strip().lower().replace(' ', '_').replace('-', '_')
                node_text.append(f"{node}: <{description}>")

        prompt = "From the text below, extract the following entities in the following format: \n"
        prompt += "\n".join(node_text)

        #         print(prompt)
        #     print('===========================')
        return prompt

    def method3(self, output_csv):

        # Find leaf nodes (nodes without children)
        leaf_nodes = [node for node in self.G.nodes() if self.G.out_degree(node) == 0]

        """generate "yes/no" question prompt"""
        if output_csv is None:

            # Generate the text for leaf nodes with descriptions
            prompt = ["From the text below, extract the following entities in the following format: \n"]
            for node in leaf_nodes:
                description = self.G.nodes[node]['description(yesno)']
                node = node.strip().lower().replace(' ', '_').replace('-', '_')
                prompt.append(f"{node}: <{description}>")

            # Create a text block with the descriptions for all leaf nodes
            prompt = "\n".join(prompt)

        else:
            """generate "what" question prompt"""

            """nodes that answer is Yes"""
            node_present = []

            for _, row in output_csv.iterrows():
                node, answer = row
                if 'yes' in answer.lower():
                    #             print('haha')
                    node_present.append(node)

            # Generate the text for leaf nodes with descriptions
            prompt = ["From the text below, extract the following entities in the following format: \n"]

            for node in leaf_nodes:
                """ only those nodes with answer YES"""
                if node in node_present:
                    description = self.G.nodes[node]['description']
                    node = node.strip().lower().replace(' ', '_').replace('-', '_')
                    prompt.append(f"{node}: <{description}>")

            # Create a text block with the descriptions for all leaf nodes
            prompt = "\n".join(prompt)

        #         print(prompt)
        return prompt

    def openai_client(self, prompt):

        max_tokens = 6000

        prompt += '\n\nText:\n'
        prompt += self.input_txt

        response = openai.ChatCompletion.create(
            # model=engine,
            deployment_id = self.deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=max_tokens)
        return response

    def parse_output(self, response):
        response_content = response['choices'][0]['message']['content']
        response_content

        # Split the input data into lines
        lines = response_content.split('\n')

        # Create a CSV file and write the data
        # with open('output.csv', 'w', newline='') as csv_file:
        #     writer = csv.writer(csv_file)

        #     for line in lines:
        #         key, value = line.split(': ')
        #         writer.writerow([key, value])

        # print("CSV file created: output.csv")

        # Create a list of dictionaries for key-value pairs
        data = [{"Key": line.split(':')[0], "Value": line.split(':')[1]} for line in lines]

        # Create a DataFrame from the list of dictionaries
        df = pd.DataFrame(data)
        return df

    def combine_output(self, dfs):

        # Step 1: Merge the dataframes
        # Assuming `dfs` is a list of your dataframes
        merged_df = pd.concat(dfs, ignore_index=True)

        # print("merged df", merged_df)

        # Step 2: Identify the leaf nodes in the graph G
        def find_leaf_nodes(G):
            return [node for node in self.G.nodes() if G.out_degree(node) == 0]

        leaf_nodes = find_leaf_nodes(self.G)
        # print('leaf nodes: ', leaf_nodes)
        # Step 3: Filter the merged dataframe to keep only leaf nodes
        filtered_df = merged_df[merged_df['Key'].isin(leaf_nodes)]

        return filtered_df

    # filtered_df = combine_output(G, df_outputs)

    def run(self):
        if self.method == 'RLS':  # method 1
            prompt = self.method1()
            response = self.openai_client(prompt)
            df_output = self.parse_output(response)
            return df_output

        if self.method == 'BFOP':  # test method 2

            G_preserve = self.G.copy()

            df_outputs = []

            for cur_layer in self.layer_nodes.keys():
                #                 print("""
                #             =================
                #             Processing layer {}
                #                 """.format(cur_layer))

                # 2. generate prompt
                prompt = self.method2(cur_layer=cur_layer)
                if prompt.endswith(" format: \n"):
                    #                     print('Done')
                    break

                # openai
                response = self.openai_client(prompt)

                # parse
                df_output = self.parse_output(response)


                # update graph
                self.update_G(df_output)

                # merge output
                df_outputs.append(df_output)

            # print('==================')
            # print('0=============:', df_outputs[0])
            #
            # print('1===========:', df_outputs[1])
            #
            # print('2==========:', df_outputs[2])
            # print('3==========:', df_outputs[3])

            merged_df = self.combine_output(df_outputs)

            self.G = G_preserve

            return merged_df

        if self.method == '2POP':
            '''# step 1: ask yes/no question'''
            prompt = self.method3(output_csv=None)
            # openai
            response = self.openai_client(prompt)
            # parse
            df_output = self.parse_output(response)

            #             print('Finish yes/no')

            '''# step 2: ask what question'''
            prompt = self.method3(df_output)
            # openai
            response = self.openai_client(prompt)
            # parse
            df_output = self.parse_output(response)
            #             print('Finish what')

            '''Step 3: complete output csv to include all leaf nodes'''

            # Find leaf nodes (nodes without children)
            leaf_nodes = [node for node in self.G.nodes() if self.G.out_degree(node) == 0]

            # 3. Create a list of missing leaf nodes
            missing_leaf_nodes = [node for node in leaf_nodes if node not in df_output['Key'].values]

            # 4. Create a DataFrame with missing leaf nodes and "NAN" as the value
            missing_df = pd.DataFrame({'Key': missing_leaf_nodes, 'Value': 'unknown'})

            # 5. Concatenate the existing DataFrame and the missing DataFrame
            df_output = pd.concat([df_output, missing_df], ignore_index=True)

            #             display(df_outputs)
            return df_output