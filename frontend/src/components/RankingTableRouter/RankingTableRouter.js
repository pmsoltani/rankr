import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { LandingPage, NotFoundPage } from '..'
import { r } from '../../routes'

const InstitutionsRouter = () => {
  return (
    <>
      <Routes>
        <Route path='/' element={<LandingPage />} />
        <Route
          path={`${r.rankingTable.url}/:rankingSystem/:year`}
          element={<LandingPage />}
        />
        <Route path='*' element={<NotFoundPage />} />
      </Routes>
    </>
  )
}

export default InstitutionsRouter
