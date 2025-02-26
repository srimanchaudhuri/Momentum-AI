import express from "express"
import {router as userRouter} from './routes/user'

const app = express()
const PORT = 3000

app.get('/', (req, res) => {
    res.send('Hi There')
})

app.use('/user', userRouter)

app.listen(PORT, () => {
    console.log('Listening on port ' + PORT);
})