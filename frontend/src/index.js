import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import '@elastic/eui/dist/eui_theme_amsterdam_light.css'

import { App } from './components'
import configureReduxStore from './redux/store'

const store = configureReduxStore()

ReactDOM.render(
  <>
    <Provider store={store}>
      <App />
    </Provider>
  </>,
  document.getElementById('root')
)
