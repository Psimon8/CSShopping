import streamlit.components.v1 as components

def st_apex_charts(chart_data):
    chart_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    </head>
    <body>
        <div id="chart"></div>
        <script>
            var options = {chart_data};
            var chart = new ApexCharts(document.querySelector("#chart"), options);
            chart.render();
        </script>
    </body>
    </html>
    """
    components.html(chart_html, height=600)
