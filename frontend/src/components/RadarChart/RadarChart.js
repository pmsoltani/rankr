import { saveAs } from 'file-saver'
import React from 'react'
import Chart from 'react-apexcharts'
import watermark from 'watermarkjs'

import { appLogoSmall, download } from '../../assets/images'
import { scoreAliases } from '../../config'
import { fileNameSafe } from '../../utils'

const RadarChart = props => {
  const {
    chartTitle = 'Score compare chart',
    categories,
    series,
    colors
  } = props
  const options = {
    chart: {
      toolbar: {
        tools: {
          download: false,
          customIcons: [
            {
              icon: `<img src="${download}" width="20">`,
              index: 0,
              title: 'Download PNG',
              class: 'custom-icon',
              click: (chart, options, e) => {
                chart.dataURI().then(({ imgURI }) => {
                  watermark([imgURI, appLogoSmall])
                    .image(watermark.image.lowerLeft(0.5))
                    .then(img =>
                      saveAs(img.src, `${fileNameSafe(chartTitle)}.png`)
                    )
                })
              }
            }
          ]
        }
      },
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
