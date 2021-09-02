import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import {
  InstitutionsRouter,
  LandingPage,
  Layout,
  NotFoundPage
} from '../../components'
import { r } from '../../routes'

const App = () => {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path={r.home.url} element={<LandingPage />} />
          <Route
            path={`${r.institutions.url}/*`}
            element={<InstitutionsRouter />}
          />
          <Route path={r.notFoundPage.url} element={<NotFoundPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
