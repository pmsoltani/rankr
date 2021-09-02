import React from 'react'
import { useNavigate } from 'react-router-dom'
import { EuiEmptyPrompt, EuiButton } from '@elastic/eui'

const NotFoundPage = ({
  notFoundItem = 'Page',
  notFoundError = "We couldn't find the page you were looking for."
}) => {
  const navigate = useNavigate()
  return (
    <EuiEmptyPrompt
      iconType='editorStrike'
      title={<h2>{notFoundItem} Not Found</h2>}
      body={<p>{notFoundError}</p>}
      actions={
        <EuiButton color='primary' fill onClick={() => navigate(-1)}>
          Go Back
        </EuiButton>
      }
    />
  )
}

export default NotFoundPage
