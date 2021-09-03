import React from 'react'
import Chart from 'react-apexcharts'

const LineChart = props => {
  const { chartTitle = 'Rank chart', categories, series, colors } = props
  const options = {
    chart: {
      id: 'rank-chart',
      toolbar: {
        export: {
          csv: { filename: chartTitle },
          png: { filename: chartTitle },
          svg: { filename: chartTitle }
        },
        tools: {
          download: true,
          pan: false,
          reset: false,
          selection: false,
          zoom: false,
          zoomin: false,
          zoomout: false
        }
      }
    },
    colors: colors,
    dataLabels: { enabled: true },
    legend: { horizontalAlign: 'right', position: 'top' },
    stroke: { width: 3 },
    title: { text: chartTitle },
    xaxis: { categories: categories },
    yaxis: { reversed: true, show: false }
  }
  return (
    <Chart
      options={options}
      series={series}
      type='line'
      width='100%'
      height='400'
    />
  )
}

export default LineChart
