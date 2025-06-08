import gradio as gr
import pandas as pd
import plotly.graph_objects as go


class GeneralMetricsDisplay:
    def __init__(self):
        self.plots = []

    @staticmethod
    def kpi_rate(percentage, title="KPI"):
        if percentage is None or not (0 <= percentage <= 100):
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                width=320,
                height=150,
                margin=dict(l=10, r=10, t=10, b=10),
                annotations=[dict(
                    text="No data",
                    showarrow=False,
                    font=dict(size=16, color="white"),
                    x=0.5, y=0.5, xanchor="center", yanchor="middle"
                )]
            )
            return fig
        fig = go.Figure(data=[go.Pie(
            values=[percentage, 100 - percentage],
            labels=['', ''],
            hole=0.6,
            marker_colors=['#2CFCFF', '#444444'],
            textinfo='none',
            hoverinfo='skip',
            sort=False,
            domain=dict(x=[0.4, 0.95], y=[0.15, 0.85])
        )])
        fig.update_layout(
            template='plotly_dark',
            annotations=[
                dict(
                    text=f"{percentage:.0f}%",
                    x=0.675, y=0.5,
                    font_size=20,
                    showarrow=False,
                    font=dict(color="white"),
                    xanchor="center", yanchor="middle"
                ),
                dict(
                    text=title,
                    x=0.05, y=0.5,
                    showarrow=False,
                    font=dict(size=16, color="white"),
                    xanchor="left", yanchor="middle"
                )
            ],
            showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
            width=320,
            height=150
        )
        return fig

    @staticmethod
    def kpi_value(value, title="Valeur"):
        width = 360
        if value is None or (isinstance(value, str) and (value.strip() == "" or value.strip().isdigit() and len(value.strip()) > 8)):
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                width=width,
                height=125,
                margin=dict(l=30, r=0, t=0, b=30),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='#111111',
                paper_bgcolor='#111111',
                annotations=[dict(
                    text="No data",
                    showarrow=False,
                    font=dict(size=16, color="white"),
                    x=0.5, y=0.5,
                    xanchor="center", yanchor="middle"
                )]
            )
            return fig
        try:
            if isinstance(value, (int, float)):
                formatted = f"{int(value)}" if float(value).is_integer() else f"{float(value):.2f}"
            else:
                td = pd.to_timedelta(value)
                total_seconds = int(td.total_seconds())
                hours, remainder = divmod(total_seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                formatted = f"{hours}h {minutes}m {seconds}s"
        except (ValueError, TypeError):
            try:
                numeric_value = float(value)
                formatted = f"{int(numeric_value)}" if numeric_value.is_integer() else f"{numeric_value:.2f}"
            except (ValueError, TypeError):
                formatted = str(value)
        fig = go.Figure()
        fig.add_annotation(
            text=f"<b>{formatted}</b>",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=24, color="white"),
            xanchor="center", yanchor="middle"
        )
        fig.add_annotation(
            text=title,
            x=0.5, y=1.8,
            showarrow=False,
            font=dict(size=16, color="lightgray"),
            xanchor="center", yanchor="middle"
        )
        fig.update_layout(
            template='plotly_dark',
            width=width,
            height=150,
            margin=dict(l=40, r=0, t=0, b=40),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            plot_bgcolor='#111111',
            paper_bgcolor='#111111'
        )
        return fig

    @staticmethod
    def get_max_part_id(df):
        if not df.empty and 'Part ID' in df.columns:
            try:
                numeric_ids = pd.to_numeric(df['Part ID'], errors='coerce')
                return int(numeric_ids.dropna().max())
            except Exception:
                return None
        return None

    @staticmethod
    def pareto(issues_df, error_col='Error Type'):
        if issues_df is None or issues_df.empty:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                annotations=[dict(
                    text="No data",
                    showarrow=False,
                    font=dict(size=16, color="white")
                )]
            )
            return fig
        issues_df['Downtime Start'] = pd.to_datetime(issues_df['Downtime Start'], errors='coerce')
        issues_df['Downtime End'] = pd.to_datetime(issues_df['Downtime End'], errors='coerce')
        issues_df['Downtime Duration'] = (issues_df['Downtime End'] - issues_df[
            'Downtime Start']).dt.total_seconds() / 60
        issues_df = issues_df.dropna(subset=['Downtime Duration'])
        grouped = issues_df.groupby(error_col)['Downtime Duration'].sum().sort_values(ascending=False)
        if grouped.empty:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                annotations=[dict(
                    text="No Error",
                    showarrow=False,
                    font=dict(size=16, color="white")
                )]
            )
            return fig
        cumulative = grouped.cumsum() / grouped.sum() * 100
        labels = grouped.index.tolist()
        durations = grouped.values
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=labels,
                y=durations,
                name='Downtime (min)',
                marker_color='#2CFCFF',
                yaxis='y1'
            )
        )
        fig.add_trace(go.Scatter(
            x=labels,
            y=cumulative,
            name='Cumulative %',
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='orange', width=2),
            marker=dict(size=8)
        ))
        fig.update_layout(
            template='plotly_dark',
            title="Pareto of errors by downtime",
            xaxis=dict(title="Errors"),
            yaxis=dict(
                title='Downtime (minutes)',
                showgrid=False,
                side='left'
            ),
            yaxis2=dict(
                title='Cumulative percentage (%)',
                overlaying='y',
                side='right',
                range=[0, 110],
                showgrid=False,
                tickformat='%'
            ),
            legend=dict(x=0.7, y=1.1),
            margin=dict(l=70, r=70, t=50, b=50),
        )
        return fig

    def general_block(self, all_tools_df, issues_df, efficiency_data):
        header = f"Metrics Summary"
        html_content = f"""
        <div style="display: flex; align-items: center; justify-content: flex-start; width: 100%;">
            <div style="flex: 0 0 2%; border-top: 1px solid white;"></div>
            <h2 style="flex: 0 0 auto; margin: 0 10px;">{header}</h2>
            <div style="flex: 1; border-top: 1px solid white;"></div>
        </div>
        """
        gr.HTML(html_content)
        with gr.Row():
            with gr.Group():
                with gr.Row(height=125):
                    total_count = gr.Plot(
                        self.kpi_value(
                            value=self.get_max_part_id(all_tools_df),
                            title="Total Count"
                        )
                    )
                    total_time = gr.Plot(
                        self.kpi_value(
                            value=efficiency_data.get("opening_time", "0 days 00:00:00"),
                            title="Total Time"
                        )
                    )
                    mtbf_plot = gr.Plot(
                        self.kpi_value(
                            value=efficiency_data.get("MTBF", "0 days 00:00:00"),
                            title="MTBF"
                        )
                    )
                    mttr_plot = gr.Plot(
                        self.kpi_value(
                            value=efficiency_data.get("MTTR", "0 days 00:00:00"),
                            title="MTTR"
                        )
                    )
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    with gr.Row(height=150):
                        oee_plot = gr.Plot(
                            self.kpi_rate(
                                percentage=efficiency_data.get('OEE', 0),
                                title="OEE"
                            )
                        )
                    with gr.Row(height=150):
                        quality_rate_plot = gr.Plot(
                            self.kpi_rate(
                                percentage=efficiency_data.get("quality_rate", 0),
                                title="Quality Rate"
                            )
                        )
                    with gr.Row(height=150):
                        availability_plot = gr.Plot(
                            self.kpi_rate(
                                percentage=efficiency_data.get("availability_rate", 0),
                                title="Availability"
                            )
                        )
            with gr.Column(scale=10):
                with gr.Group():
                    with gr.Row(height=450):
                        pareto = gr.Plot(
                            self.pareto(issues_df, error_col='Error Code')
                        )
        self.plots = [
            total_count, total_time,
            oee_plot, quality_rate_plot, availability_plot,
            mtbf_plot, mttr_plot,
            pareto,
        ]
        return self.plots

    def refresh(self, all_tools_df, issues_df, efficiency_data):
        return [
            self.kpi_value(value=self.get_max_part_id(all_tools_df), title="Total Count"),
            self.kpi_value(value=efficiency_data.get("opening_time", "0 days 00:00:00"), title="Total Time"),
            self.kpi_rate(percentage=efficiency_data.get('OEE', 0), title="OEE"),
            self.kpi_rate(percentage=efficiency_data.get("quality_rate", 0), title="Quality Rate"),
            self.kpi_rate(percentage=efficiency_data.get("availability_rate", 0), title="Availability"),
            self.kpi_value(value=efficiency_data.get("MTBF", "0 days 00:00:00"), title="MTBF"),
            self.kpi_value(value=efficiency_data.get("MTTR", "0 days 00:00:00"), title="MTTR"),
            self.pareto(issues_df, error_col='Error Code')
        ]