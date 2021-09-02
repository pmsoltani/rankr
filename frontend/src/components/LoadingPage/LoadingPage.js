import React from 'react'
import {
  EuiFlexGroup,
  EuiFlexItem,
  EuiLoadingSpinner,
  EuiText
} from '@elastic/eui'

const LoadingPage = props => {
  const { message = 'getting it...', spinnerSize = 'xl' } = props
  return (
    <EuiFlexGroup direction='column' alignItems='center'>
      <EuiFlexItem grow={false}>
        <EuiLoadingSpinner size={spinnerSize} />
      </EuiFlexItem>
      <EuiFlexItem grow={false}>
        {message && <EuiText textAlign='center'>{message}</EuiText>}
      </EuiFlexItem>
    </EuiFlexGroup>
  )
}

export default LoadingPage
