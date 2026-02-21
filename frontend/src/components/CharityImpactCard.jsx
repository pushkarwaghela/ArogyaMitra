import { motion } from 'framer-motion'
import { Heart, TrendingUp, Award } from 'lucide-react'

const CharityImpactCard = ({ totalWorkouts, streak, caloriesBurned }) => {
    // Calculate impact metrics
    const mealsProvided = Math.floor(caloriesBurned / 500) // 500 calories = 1 meal
    const treesPlanted = Math.floor(totalWorkouts / 10) // 10 workouts = 1 tree
    const vaccineDoses = Math.floor(streak / 7) // 7-day streak = 1 vaccine dose

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="bg-gradient-to-br from-rose-500 to-orange-500 rounded-2xl shadow-lg p-6 text-white"
        >
            <div className="flex items-center gap-3 mb-4">
                <div className="bg-white/20 p-3 rounded-full">
                    <Heart className="w-6 h-6" />
                </div>
                <div>
                    <h2 className="text-xl font-semibold">Your Impact</h2>
                    <p className="text-sm opacity-90">Fitness for a cause</p>
                </div>
            </div>

            <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="text-center">
                    <div className="bg-white/20 rounded-lg p-2 mb-1">
                        <Award className="w-6 h-6 mx-auto" />
                    </div>
                    <p className="text-2xl font-bold">{mealsProvided}</p>
                    <p className="text-xs opacity-90">Meals Provided</p>
                </div>
                <div className="text-center">
                    <div className="bg-white/20 rounded-lg p-2 mb-1">
                        <TrendingUp className="w-6 h-6 mx-auto" />
                    </div>
                    <p className="text-2xl font-bold">{treesPlanted}</p>
                    <p className="text-xs opacity-90">Trees Planted</p>
                </div>
                <div className="text-center">
                    <div className="bg-white/20 rounded-lg p-2 mb-1">
                        <Heart className="w-6 h-6 mx-auto" />
                    </div>
                    <p className="text-2xl font-bold">{vaccineDoses}</p>
                    <p className="text-xs opacity-90">Vaccine Doses</p>
                </div>
            </div>

            <p className="text-sm text-center opacity-90">
                Keep working out to make a difference! 💪
            </p>
        </motion.div>
    )
}

export default CharityImpactCard