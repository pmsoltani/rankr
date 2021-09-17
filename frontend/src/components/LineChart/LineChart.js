import { saveAs } from 'file-saver'
import React from 'react'
import Chart from 'react-apexcharts'
import watermark from 'watermarkjs'

import { appLogoSmall, download } from '../../assets/images'
import { fileNameSafe } from '../../utils'

const LineChart = props => {
  const { chartTitle = 'Rank chart', categories, series, colors } = props
  const options = {
    chart: {
      id: 'rank-chart',
      toolbar: {
        tools: {
          download: false,
          pan: false,
          reset: false,
          selection: false,
          zoom: false,
          zoomin: false,
          zoomout: false,
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
      }
    },
    colors: colors,
    dataLabels: { enabled: true },
    legend: { horizontalAlign: 'right', position: 'top' },
    stroke: { width: 3 },
    title: { text: chartTitle },
    tooltip: {
      y: {
        formatter: (val, { seriesIndex, dataPointIndex, w }) => {
          const rawValue = w.config.series[seriesIndex].rawData[dataPointIndex]
          if (rawValue) return rawValue
        }
      }
    },
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
