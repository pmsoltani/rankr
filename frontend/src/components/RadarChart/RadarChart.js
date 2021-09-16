import React from 'react'
import Chart from 'react-apexcharts'

import { scoreAliases } from '../../config'

const RadarChart = props => {
  const {
    chartTitle = 'Score compare chart',
    categories,
    series,
    colors
  } = props
  const options = {
    chart: {
      height: 350,
      type: 'radar',
      dropShadow: { enabled: true, blur: 1, left: 1, top: 1 }
    },
    colors: colors,
    fill: { opacity: 0.1 },
    legend: { horizontalAlign: 'right', position: 'top' },
    stroke: { width: 2 },
    title: { text: chartTitle },
    tooltip: {
      x: {
        formatter: (value, { dataPointIndex, w }) => {
          const rankingSystem = w.config.series[0].rankingSystem
          const fullMetric = Object.keys(
            scoreAliases[rankingSystem.toLowerCase()]
          ).find(
            key => scoreAliases[rankingSystem.toLowerCase()][key] === value
          )
          return fullMetric
        }
      },
      y: {
        formatter: (val, { seriesIndex, dataPointIndex, w }) => {
          const rawValue = w.config.series[seriesIndex].rawData[dataPointIndex]
          if (rawValue) return rawValue
        }
      }
    },
    xaxis: { categories: categories },
    yaxis: { min: 0, max: 100, tickAmount: 5 }
  }
  return (
    <Chart
      options={options}
      series={series}
      type='radar'
      width='100%'
      height='400'
    />
  )
}

export default RadarChart
