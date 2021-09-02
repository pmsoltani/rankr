import { configureStore, getDefaultMiddleware } from '@reduxjs/toolkit'

import rootReducer from './reducers/rootReducer'

export default function configureReduxStore () {
  const store = configureStore({
    reducer: rootReducer,
    middleware: [...getDefaultMiddleware()]
  })

  // enable hot reloading in development
  if (process.env.NODE_ENV !== 'prod' && module.hot) {
    module.hot.accept('./reducers/rootReducer', () =>
      store.replaceReducer(rootReducer)
    )
  }

  return store
}
