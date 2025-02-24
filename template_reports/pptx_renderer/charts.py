from pptx.chart.data import ChartData

from template_reports.templating.core import process_text


def process_chart(chart, context, perm_user):
    """
    Read the current chart data, format text fields using the provided context,
    then update the chart with the new data.

    Parameters:
        chart: a pptx.chart.chart.Chart object.
        context: a dict used for formatting placeholders in text values.
        perm_user: passed along for consistency (not used in this example).
    """

    def _process_text(t):
        return process_text(
            t,
            context,
            perm_user,
            mode="normal",
        )

    # 1. Read the categories from the first plot.
    # Note: This assumes the chart has at least one plot.
    plot = chart.plots[0]

    # Categories is a sequence of Category objects; convert to list of strings and process the templating.
    categories = [_process_text(str(cat)) for cat in plot.categories]

    # 2. Read the series data.
    # chart.series is a SeriesCollection containing all series in the chart.
    series_data = []
    for series in chart.series:
        # Read the series name and values.
        placeholder_name = series.name

        # Process templating of the series name if it is a string with placeholders.
        name = (
            _process_text(placeholder_name)
            if isinstance(placeholder_name, str)
            else placeholder_name
        )

        # The series values are a sequence of floats.
        values = list(series.values)
        series_data.append((name, values))

    # 3. Create a new ChartData object and populate it.
    chart_data = ChartData()
    chart_data.categories = categories
    for name, values in series_data:
        chart_data.add_series(name, values)

    # 4. Replace the chart’s data with the new ChartData.
    chart.replace_data(chart_data)
