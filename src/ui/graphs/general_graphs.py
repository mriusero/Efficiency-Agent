import gradio as gr
import plotly.express as px

class GeneralMetricsDisplay:
    def __init__(self):
        self.plot_all_tools = gr.Plot()
        self.plot_issues = gr.Plot()
        self.plot_efficiency = gr.Plot()

    def block(self, all_tools_df, issues_df, efficiency_data):
        return [self.plot_all_tools, self.plot_issues, self.plot_efficiency]

    def update(self, all_tools_df, issues_df, efficiency_data):
        #fig_all = px.scatter(tools_df, x="Position", y="Orientation", color="Compliance", title="All Tools Summary")
        #fig_issues = px.histogram(issues_df, x="Error Description", title="Error Types Distribution")
        #fig_eff = px.bar(x=list(efficiency_data.keys()), y=list(efficiency_data.values()), title="Machine Efficiency")
        #return [fig_all, fig_issues, fig_eff]
        return self.plot_all_tools, self.plot_issues, self.plot_efficiency
