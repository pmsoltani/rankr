import React from 'react'
import {
  EuiBadge,
  EuiBasicTable,
  EuiFlexGroup,
  EuiFlexItem
} from '@elastic/eui'
import styled from 'styled-components'

import { InstitutionLogo, StyledLink } from '..'
import { r } from '../../routes'

const StyledBadge = styled(EuiBadge)`
  background-color: rgb(211, 218, 230);
  border: solid 1px transparent;
  border-radius: 3px;
  color: black;
  font-size: 12px;
  font-weight: 500;
  line-height: 18px;
  padding: 0 4px;
`

const RankingTable = props => {
  const { isLoading, data } = props
  const columns = [
    {
      align: 'center',
      field: 'raw_value',
      name: 'Rank',
      render: rank => <StyledBadge>{rank}</StyledBadge>,
      sortable: true,
      width: '15%'
    },
    {
      align: 'center',
      field: 'institution',
      name: 'Country',
      render: inst => {
        const countryCode = inst.country.country_code.toLowerCase()
        return (
          <div
            className={`flag-icon flag-icon-${countryCode}`}
            title={inst.country.country}
            aria-label={`Flag of ${inst.country.country}`}
            style={{ fontSize: '1.2em' }}
          />
        )
      },
      width: '15%'
    },
    {
      field: 'institution',
      name: 'Institution',
      render: inst => {
        return (
          <>
            <EuiFlexGroup alignItems='center'>
              <EuiFlexItem grow={false}>
                <InstitutionLogo
                  alt={`${inst.name} logo`}
                  key={inst.grid_id}
                  institution={inst}
                />
              </EuiFlexItem>
              <EuiFlexItem>
                <StyledLink to={`${r.institutions.url}/${inst.grid_id}`}>
                  {inst.name}
                </StyledLink>
              </EuiFlexItem>
            </EuiFlexGroup>
          </>
        )
      },
      sortable: true
    }
  ]
  const [tableItems, setTableItems] = React.useState([])
  const [offset, setOffset] = React.useState(0)
  const [limit, setLimit] = React.useState(10)
  const [sortField, setSortField] = React.useState('raw_value')
  const [sortDirection, setSortDirection] = React.useState('asc')
  const [rankingSystem, setRankingSystem] = React.useState(null)
  const [year, setYear] = React.useState(null)

  const onTableChange = ({ page = {}, sort = {} }) => {
    setOffset(page.index)
    setLimit(page.size)
    setSortField(sort.field)
    setSortDirection(sort.direction)
  }

  const pagination = {
    pageIndex: offset,
    pageSize: limit,
    totalItemCount: data.length,
    pageSizeOptions: [10, 25, 50],
    hidePerPageOptions: false
  }

  const sorting = {
    sort: {
      field: sortField,
      direction: sortDirection
    }
  }

  React.useEffect(() => {
    if (data.length) {
      setRankingSystem(data[0].ranking_system)
      setYear(data[0].year)
    }
  }, [data])

  React.useEffect(() => setOffset(0), [rankingSystem, year])

  React.useEffect(() => {
    if (data.length) {
      const start = limit * offset
      const slice = data
        .sort((a, b) => {
          if (sortField === 'institution') {
            return sortDirection === 'asc'
              ? a[sortField].name.localeCompare(b[sortField].name)
              : b[sortField].name.localeCompare(a[sortField].name)
          }
          if (sortField === 'raw_value') {
            let result
            if (a.value === null) {
              result = 1
            } else if (b.value === null) {
              result = -1
            } else {
              result = a.value - b.value
            }
            return sortDirection === 'asc' ? result : -result
          }
          return sortDirection === 'asc' ? a - b : b - a
        })
        .slice(start, start + limit)

      setTableItems(slice)
    }
  }, [offset, limit, data, sortField, sortDirection])

  return (
    <EuiBasicTable
      columns={columns}
      compressed={false}
      items={isLoading ? [] : tableItems}
      loading={isLoading}
      onChange={onTableChange}
      pagination={pagination}
      responsive
      rowHeader='institution'
      noItemsMessage={isLoading ? 'Getting it...' : 'No items found'}
      sorting={sorting}
      tableLayout='fixed'
    />
  )
}

export default RankingTable
