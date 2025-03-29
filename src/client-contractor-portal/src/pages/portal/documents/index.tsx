import { Folder } from '@mui/icons-material'
import { Table, TableHead, TableRow, TableCell, TableBody, Box, Typography, Container } from '@mui/material'
import { useRouter } from 'next/router'
import React from 'react'
import PortalLayout from '@/components/layouts/PortalLayout'

export default function Documents() {
  const router = useRouter();
  return (
    <Container>
      <Table sx={{ mb: 6 }}> {/* Added right-click handler */}
        <TableHead>
          <TableRow>
            <TableCell>Name</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow onClick={() => router.push(`${router.asPath}/general`)}>
            <TableCell align='center' >
              <Box display="flex" alignItems="center" >
                <Folder />
                <Typography sx={{ display: "inline", marginLeft: 1, mt: "5px", cursor: "pointer" }} variant='body1'>
                  General Documents
                </Typography>
              </Box>
            </TableCell>
          </TableRow>

          <TableRow onClick={() => router.push(`${router.asPath}/specific`)}>
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
    </Container>
  )
}

Documents.getLayout = function getLayout(page: React.ReactElement) {
  return <PortalLayout>{page}</PortalLayout>
}
