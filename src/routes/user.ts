import express from 'express'
import prisma from '../db'

export const router = express.Router()

router.get("/", async (req, res) => {
    const users = await prisma.user.findMany()
    res.json({
        users
    })
})

router.post("/signup", async (req, res) => {
    
})