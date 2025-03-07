import { Folder } from '@mui/icons-material'
import { Table, TableHead, TableRow, TableCell, TableBody, Box, Typography } from '@mui/material'
import { useRouter } from 'next/router'
import React from 'react'

const Documents = () => {
  const router = useRouter();
  return (
    <Table sx={{ mb: 6 }}> {/* Added right-click handler */}
      <TableHead>
        <TableRow>
          <TableCell>Name</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        <TableRow onClick={()=>router.push(`${router.asPath}/sitewide`)}>
          <TableCell align='center' >
            <Box display="flex" alignItems="center" >
              <Folder />
              <Typography sx={{ display: "inline", marginLeft: 1, mt: "5px", cursor: "pointer" }} variant='body1'>
                General Documents
              </Typography>
            </Box>
          </TableCell>
        </TableRow>

        <TableRow onClick={()=>router.push(`${router.asPath}/sitespecific`)}>
          <TableCell align='center' >
            <Box display="flex" alignItems="center" >
              <Folder />
              <Typography sx={{ display: "inline", marginLeft: 1, mt: "5px", cursor: "pointer" }} variant='body1'>
                Site Related Documents
              </Typography>
            </Box>
          </TableCell>
        </TableRow>

      </TableBody>
    </Table>

  )
}

export default Documents