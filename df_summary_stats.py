from typing import Literal

import numpy as np
import pandas as pd
import streamlit as st

@st.fragment
def show_summary_stats(
    data: pd.DataFrame,
    column: str,
    column_label: str | None = None,
    display_type: Literal["dialog", "main", "side-by-side"] = "dialog",
    height: str | None = None,
) -> None:
    def _title(
        type_icon: str,
        type_name: str,
    ) -> None:
        st.caption(
            f":gray-background[ {type_icon + '  ' if type_icon else ''}{type_name} column summary ]",
        )
        st.caption("")

    def _show_summary_stats(data: pd.DataFrame, column: str):
        import plotly.express as px

        col_data: pd.Series = data[column]
        value_counts: pd.DataFrame = (
            col_data.value_counts(dropna=False)
            .reset_index()
            .rename(columns={column: "Category", "count": "Count"})
            .assign(Percentage=lambda x: x["Count"] * 100.0 / x["Count"].sum())
        )
        num_unique_values: int = col_data.nunique()
        num_total_values: int = len(col_data)
        percent_null_values: float = round(col_data.isnull().mean() * 100, 1)

        if (
            pd.api.types.is_categorical_dtype(col_data)
            or pd.api.types.is_object_dtype(col_data)
            or pd.api.types.is_bool_dtype(col_data)
        ):
            if pd.api.types.is_bool_dtype(col_data):
                _title(":material/toggle_on:", "Boolean")
            else:
                _title(":material/category:", "Categorical")

            left, right = st.columns((1, 5))
            left.metric("Unique values", num_unique_values)
            left.metric("Total values", num_total_values)
            left.metric("Null values (%)", percent_null_values)

            with right:

                def _get_label(row):
                    return f"<b>{row['Category']}</b>  ·  {row.Count} <br>({row['Percentage']:.1f}%)"

                value_counts["Label"] = value_counts.apply(_get_label, axis=1)

                fig = px.bar(
                    data_frame=value_counts,
                    x="Category",
                    y="Count",
                    text="Label",
                    color="Category",
                    color_discrete_sequence=px.colors.qualitative.Plotly,
                    height=300,
                )

                fig.update_layout(
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(
                        automargin=False,
                        title_text="",
                        showgrid=False,
                    ),
                    yaxis=dict(
                        automargin=False,
                        title_text="",
                        showgrid=False,
                        showticklabels=False,
                    ),
                )

                fig.update_traces(
                    textposition="inside",
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    height=50,
                )

        elif pd.api.types.is_numeric_dtype(col_data):
            _title(":material/123:", "Numerical")
            stats = {
                "Unique values": col_data.nunique(),
                "Null values (%)": round(col_data.isnull().mean() * 100, 1),
                "Max": col_data.max(),
                "Mean": col_data.mean(),
                "Median": col_data.median(),
                "Min": col_data.min(),
            }

            stats_df = pd.DataFrame(stats, index=[0])

            st.dataframe(
                stats_df,
                use_container_width=True,
                hide_index=True,
            )

            left, right = st.columns((2, 4))

            # Boxplot

            fig = px.box(col_data, height=200)

            fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(
                    automargin=False,
                    title_text="",
                    showgrid=False,
                ),
                yaxis=dict(
                    automargin=False,
                    title_text="",
                    showgrid=False,
                    showticklabels=True,
                ),
                hovermode="x",
            )

            left.plotly_chart(
                fig, use_container_width=True, config={"displayModeBar": False}
            )

            num_bins = min(int(np.ceil(np.log2(len(data)) + 1)), col_data.nunique())

            def _get_label(row):
                return f"<b>{row['Category']}</b> <br>{row['Count']}"

            binned_data: pd.DataFrame = (
                col_data.value_counts(
                    bins=num_bins,
                    dropna=False,
                    sort=False,
                )
                .reset_index()
                .rename(columns={"index": "Category", "count": "Count"})
                .assign(Percentage=lambda x: x["Count"] * 100.0 / x["Count"].sum())
                .assign(
                    Category=lambda x: x["Category"].map(
                        lambda x: f"From {x.left:.1f} to {x.right:.2f}"
                    )
                )
                .assign(Label=lambda x: x.apply(_get_label, axis=1))
            )

            fig = px.bar(
                data_frame=binned_data,
                x="Category",
                y="Count",
                text="Count",
            )

            fig.update_layout(
                showlegend=False,
                hoverlabel=dict(font_size=14),
                hovermode="x",
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(
                    automargin=False,
                    showgrid=False,
                    title_text="",
                    showticklabels=False,
                ),
                yaxis=dict(
                    automargin=False,
                    showgrid=True,
                    title_text="",
                    showticklabels=True,
                ),
                height=200,
                modebar=None,
            )

            fig.update_traces(
                textposition="inside",
                textfont_size=12,
                hovertemplate="%{x} <br>Num. values = %{y} (%{customdata[0]:.1f}%)",
                customdata=binned_data[["Percentage"]].values,
            )

            right.plotly_chart(fig, use_container_width=True)

        elif pd.api.types.is_datetime64_any_dtype(col_data):
            _title(":material/calendar_month:", "Datetime")

            stats = {
                "Earliest date": col_data.min(),
                "Latest date": col_data.max(),
                "Unique values": col_data.nunique(),
                "Null values (%)": round(col_data.isnull().mean() * 100, 1),
            }

            st.dataframe(
                pd.DataFrame(stats, index=[0]),
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Earliest date": st.column_config.DateColumn("Earliest date"),
                    "Latest date": st.column_config.DateColumn("Latest date"),
                },
            )

            left, right = st.columns((1, 2.5))

            # Count day of weeks
            day_of_week = col_data.dt.day_name()
            day_of_week_counts = day_of_week.value_counts().reset_index()
            day_of_week_counts.columns = ["Day of week", "Count"]
            left.dataframe(day_of_week_counts.set_index("Day of week"), height=200)

            # Date histogram
            fig = px.histogram(
                data,
                x=column,
                height=200,
            )

            fig.update_layout(
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(
                    automargin=False,
                    title_text="",
                    showgrid=False,
                ),
                yaxis=dict(
                    automargin=False,
                    title_text="",
                    showgrid=False,
                    showticklabels=False,
                ),
                bargap=0.5,
            )

            right.plotly_chart(fig, use_container_width=True)

    if display_type == "dialog":

        @st.dialog(column_label or column, width="large")
        def _show_summary_stats_dialog():
            _show_summary_stats(data, column)

        _show_summary_stats_dialog()

    elif display_type == "main":
        with st.container(border=True, height=height):
            _show_summary_stats(data, column)


def dataframe_with_summary_stats(
    data: pd.DataFrame,
    display_type: Literal["dialog", "main", "side-by-side"] = "dialog",
    height: int = 400,  # Useful for "main" and "side-by-side"
    **kwargs,
) -> None:
    assert (
        "selection_mode" not in kwargs
    ), "Argument selection_mode is already in use in dataframe_with_summary_stats"

    assert (
        "on_select" not in kwargs
    ), "Argument on_select is already in use in dataframe_with_summary_stats"

    if display_type == "side-by-side":
        left, right = st.columns(2)
        container = left.empty()
    else:
        container = st.empty()

    selection = container.dataframe(
        data=data,
        on_select="rerun",
        selection_mode="single-column",
        **kwargs,
    )

    if selected_columns := selection["selection"].get("columns"):
        selected_column = selected_columns[0]

        if display_type == "side-by-side":
            with right:
                show_summary_stats(
                    data,
                    selected_column,
                    display_type="main",
                    height=height,
                )
        else:
            show_summary_stats(
                data,
                selected_column,
                display_type=display_type,
                height=height,
            )
