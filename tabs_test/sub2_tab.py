from table_tab import TableTab

class Sub2Tab(TableTab):
    def __init__(self, input_csv):
        super().__init__(input_csv)

        # overwride super class field
        self.target_column = "gl_vars" # args or gl_vars
        self.target_columns = ["type", self.target_column, "value"]
        self.output_csv_file_name = "gl_vars.csv"
        
        # create table widgets and set layout
        self.createLabel(f"file_name(default): {self.output_csv_file_name}")
        self.createTable(self.input_df, self.target_columns)
        self.updateLayout()
