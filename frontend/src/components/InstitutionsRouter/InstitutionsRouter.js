import React from 'react'
import { Routes, Route } from 'react-router-dom'

import { InstitutionPage, NotFoundPage } from '..'

const InstitutionsRouter = () => {
  return (
    <>
      <Routes>
        <Route path='/' element={<NotFoundPage />} />
        <Route path=':institutionID' element={<InstitutionPage />} />
        <Route path='*' element={<NotFoundPage />} />
      </Routes>
    </>
  )
}

export default InstitutionsRouter
