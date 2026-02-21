import { motion } from 'framer-motion'

const BackgroundImage = () => {
    return (
        <div className="fixed inset-0 -z-10 overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-white to-green-50" />
            <motion.div
                className="absolute top-20 left-10 w-72 h-72 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
                animate={{
                    x: [0, 100, 0],
                    y: [0, 50, 0],
                }}
                transition={{
                    duration: 20,
                    repeat: Infinity,
                    ease: "linear"
                }}
            />
            <motion.div
                className="absolute bottom-20 right-10 w-96 h-96 bg-green-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
                animate={{
                    x: [0, -100, 0],
                    y: [0, -50, 0],
                }}
                transition={{
                    duration: 25,
                    repeat: Infinity,
                    ease: "linear"
                }}
            />
            <motion.div
                className="absolute top-40 right-40 w-60 h-60 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-70"
                animate={{
                    x: [0, 50, 0],
                    y: [0, -100, 0],
                }}
                transition={{
                    duration: 18,
                    repeat: Infinity,
                    ease: "linear"
                }}
            />
        </div>
    )
}

export default BackgroundImage