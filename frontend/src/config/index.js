import {
  qsColor,
  qsDisabled,
  shanghaiColor,
  shanghaiDisabled,
  theColor,
  theDisabled
} from '../assets/images'

export const APP_ENV = process.env.REACT_APP_APP_ENV || 'dev'
export const APP_NAME = process.env.REACT_APP_APP_NAME || 'rankr'
export const APP_URL = process.env.REACT_APP_APP_URL
export const REMOTE_SERVER_URL = process.env.REACT_APP_REMOTE_SERVER_URL
export const SERVER_HOST = process.env.REACT_APP_SERVER_HOST || 'localhost'
export const SERVER_PORT = process.env.REACT_APP_SERVER_PORT || 8000
export const SERVER_API_V1_STR =
  process.env.REACT_APP_SERVER_API_V1_STR || '/api/v1'

export const gridBase = 'https://www.grid.ac/'
export const openStreetMapBase = 'https://www.openstreetmap.org/'

export const rankingSystems = {
  qs: {
    alias: 'QS',
    color: '#feb019',
    icon: qsColor,
    iconDisabled: qsDisabled
  },
  shanghai: {
    alias: 'Shanghai',
    color: '#ff4560',
    icon: shanghaiColor,
    iconDisabled: shanghaiDisabled
  },
  the: {
    alias: 'THE',
    color: '#008ffb',
    icon: theColor,
    iconDisabled: theDisabled
  }
}

export const scoreAliases = {
  qs: {
    'Overall Score': 'Overall',
    'Academic Reputation Score': 'Academic Rep.',
    'Employer Reputation Score': 'Employer Rep.',
    'Faculty Student Score': 'Faculty Student',
    'International Faculty Score': 'Intl. Faculty',
    'International Students Score': 'Intl. Student',
    'Citations per Faculty Score': 'Cite/Faculty',
    'Citations per Paper Score': 'Cite/Paper',
    'H-index Citations Score': 'H-index Cite'
  },
  shanghai: {
    'Overall Score': 'Overall',
    'Alumni Score': 'Alumni',
    'Award Score': 'Award',
    'HiCi Score': 'HiCi',
    'N&S Score': 'N&S',
    'PUB Score': 'PUB',
    'PCP Score': 'PCP',
    'CNCI Score': 'CNCI',
    'IC Score': 'IC',
    'TOP Score': 'TOP',
    'Q1 Score': 'Q1'
  },
  the: {
    'Overall Score': 'Overall',
    'Teaching Score': 'Teaching',
    'Research Score': 'Research',
    'Citations Score': 'Citations',
    'Industry Income Score': 'Ind. Income',
    'International Outlook Score': 'Intl. Outlook'
  }
}
