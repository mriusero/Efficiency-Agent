import gradio as gr
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm


class ToolMetricsDisplay:
    def __init__(self):
        self.df = None
        self.pos_color = '#2CFCFF'
        self.ori_color = '#ff8508'
        self.plots = []

    @staticmethod
    def gauge(df, type=None, cote=None):
        if df is None or df.empty:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                width=200,
                height=170,
                margin=dict(l=30, r=50, t=30, b=0),
                annotations=[dict(
                    text="No data available",
                    showarrow=False,
                    font=dict(size=16, color="white")
                )]
            )
            return fig

        column = f"{cote}_rolling_{type}"
        idx = df['Timestamp'].idxmax()
        value = df.loc[idx, column]
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=value,
            number={'font': {'color': 'white', 'size': 20}},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': type, 'font': {'color': 'white', 'size': 16}},
            gauge={'axis': {'range': [0, 3]},
                   'bar': {'color': 'black', 'thickness': 0.4},
                   'steps': [
                       {'range': [0, 1.33], 'color': "red"},
                       {'range': [1.33, 2], 'color': "yellow"},
                       {'range': [2, 3], 'color': "green"}],
                   'threshold': {
                       'line': {'color': 'black', 'width': 3},
                       'thickness': 0.8,
                       'value': value}}
        ))
        fig.update_layout(
            template='plotly_dark',
            width=200,
            height=170,
            margin=dict(l=30, r=50, t=30, b=0),
        )
        return fig

    def control_graph(self, df):
        if df is None or df.empty:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                xaxis_title='Timestamp',
                yaxis_title='Valeurs',
                showlegend=True,
                width=720,
                height=400,
                margin=dict(l=70, r=10, t=30, b=70),
                annotations=[dict(
                    text="No data available",
                    showarrow=False,
                    font=dict(size=20, color="white")
                )]
            )
            return fig

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=[0.3] * len(df), mode='lines',
                                 line=dict(dash='dot', color=self.pos_color, width=1), name='lsl pos'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=[0.5] * len(df), mode='lines',
                                 line=dict(dash='dot', color=self.pos_color, width=1), name='usl pos'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=[0.2] * len(df), mode='lines',
                                 line=dict(dash='dot', color=self.ori_color, width=1), name='lsl ori'))
        fig.add_trace(go.Scatter(x=df['Timestamp'], y=[0.6] * len(df), mode='lines',
                                 line=dict(dash='dot', color=self.ori_color, width=1), name='usl ori'))
        fig.add_trace(
            go.Scatter(x=df['Timestamp'], y=df['Position'], mode='lines+markers', line=dict(color=self.pos_color),
                       name='pos'))
        fig.add_trace(
            go.Scatter(x=df['Timestamp'], y=df['Orientation'], mode='lines+markers', line=dict(color=self.ori_color),
                       name='ori'))
        fig.update_layout(
            template='plotly_dark',
            xaxis_title='Timestamp',
            yaxis_title='Valeurs',
            showlegend=True,
            width=720,
            height=400,
            margin=dict(l=70, r=10, t=30, b=70)
        )
        return fig

    def normal_curve(self, df, cote=None):
        if df is None or df.empty:
            fig = go.Figure()
            fig.update_layout(
                template='plotly_dark',
                showlegend=False,
                width=370,
                height=250,
                margin=dict(l=40, r=40, t=40, b=40),
                annotations=[dict(
                    text="No data available",
                    showarrow=False,
                    font=dict(size=16, color="white")
                )]
            )
            return fig

        if cote == 'pos':
            color = self.pos_color
            lsl = 0.3
            usl = 0.5
        else:
            color = self.ori_color
            lsl = 0.2
            usl = 0.6
        mu_column = f"{cote}_rolling_mean"
        std_column = f"{cote}_rolling_std"
        idx = df['Timestamp'].idxmax()
        mu, std = df.loc[idx, [mu_column, std_column]]
        x = np.linspace(mu - 3 * std, mu + 3 * std, 100)
        y = norm.pdf(x, mu, std)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Normal Curve', line=dict(color=color)))
        fig.add_shape(type="line", x0=usl, y0=0, x1=usl, y1=max(y), line=dict(color="red", width=1, dash="dot"),
                      name='usl')
        fig.add_shape(type="line", x0=lsl, y0=0, x1=lsl, y1=max(y), line=dict(color="red", width=1, dash="dot"),
                      name='lsl')
        fig.update_layout(
            template='plotly_dark',
            showlegend=False,
            width=370,
            height=250,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        return fig

    def tool_block(self, df, id=1):
        header = f"Tool {id}"
        html_content = f"""
        <div style="display: flex; align-items: center; justify-content: flex-start; width: 100%;">
            <div style="flex: 0 0 2%; border-top: 1px solid white;"></div>
            <h2 style="flex: 0 0 auto; margin: 0 10px;">{header}</h2>
            <div style="flex: 1; border-top: 1px solid white;"></div>
        </div>
        """
        gr.HTML(html_content)
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### `Position`")
                with gr.Group():
                    with gr.Row(height=250):
                        pos_normal_plot = gr.Plot(self.normal_curve(df=df, cote='pos'))
                    with gr.Row(height=150):
                        pos_cp_gauge = gr.Plot(self.gauge(df=df, type='cp', cote='pos'))
                        pos_cpk_gauge = gr.Plot(self.gauge(df=df, type='cpk', cote='pos'))
            with gr.Column(scale=1):
                gr.Markdown("### `Orientation`")
                with gr.Group():
                    with gr.Row(height=250):
                        ori_normal_plot = gr.Plot(self.normal_curve(df=df, cote='ori'))
                    with gr.Row(height=150):
                        ori_cp_gauge = gr.Plot(self.gauge(df=df, type='cp', cote='ori'))
                        ori_cpk_gauge = gr.Plot(self.gauge(df=df, type='cpk', cote='ori'))
            with gr.Column(scale=2):
                gr.Markdown("### `Control card`")
                with gr.Row(height=400):
                    control_plot = gr.Plot(self.control_graph(df=df))

            self.plots = [
                pos_normal_plot, pos_cp_gauge, pos_cpk_gauge,
                ori_normal_plot, ori_cp_gauge, ori_cpk_gauge,
                control_plot
            ]
            return self.plots