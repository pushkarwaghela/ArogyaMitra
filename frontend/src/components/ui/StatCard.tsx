import React from 'react'
import { motion } from 'framer-motion'
import { DivideIcon as LucideIcon } from 'lucide-react'

interface StatCardProps {
    title: string
    value: number | string
    unit?: string
    icon: LucideIcon
    color: 'blue' | 'green' | 'orange' | 'purple' | 'red'
    change?: string
}

const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    orange: 'bg-orange-100 text-orange-600',
    purple: 'bg-purple-100 text-purple-600',
    red: 'bg-red-100 text-red-600'
}

const StatCard: React.FC<StatCardProps> = ({
    title,
    value,
    unit,
    icon: Icon,
    color,
    change
}) => {
    return (
        <motion.div
            whileHover={{ scale: 1.02 }}
            className="bg-white rounded-2xl shadow-lg p-6"
        >
            <div className="flex items-start justify-between mb-2">
                <div className={`p-3 rounded-xl ${colorClasses[color]}`}>
                    <Icon className="w-6 h-6" />
                </div>
                {change && (
                    <span className="text-green-600 text-sm font-medium">{change}</span>
                )}
            </div>

            <h3 className="text-gray-500 text-sm mb-1">{title}</h3>
            <div className="flex items-baseline gap-1">
                <span className="text-3xl font-bold text-gray-800">{value}</span>
                {unit && <span className="text-gray-500 text-sm">{unit}</span>}
            </div>
        </motion.div>
    )
}

export default StatCard