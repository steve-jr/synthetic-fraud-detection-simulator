import random
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import numpy as np
from faker import Faker
import logging
from flask import Flask, render_template, request, jsonify
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

class FraudPattern(Enum):
    RAPID_FIRE = "rapid_fire"
    GEOGRAPHIC_HOPPING = "geographic_hopping"
    DEVICE_SPOOFING = "device_spoofing"
    AMOUNT_ESCALATION = "amount_escalation"
    MERCHANT_CYCLING = "merchant_cycling"
    VELOCITY_ATTACK = "velocity_attack"
    ACCOUNT_TAKEOVER = "account_takeover"
    MIXED_PATTERNS = "mixed_patterns"

@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    merchant_id: str
    merchant_category: str
    timestamp: str
    device_fingerprint: str
    ip_address: str
    location: Dict[str, Any]
    payment_method: str
    is_synthetic: bool = True
    fraud_pattern: Optional[str] = None
    risk_score: Optional[float] = None

class SyntheticFraudSimulator:
    def __init__(self):
        self.faker = Faker()
        self.transactions: List[Transaction] = []
        self.users: Dict[str, Dict] = {}
        self.merchants: Dict[str, Dict] = {}
        self.device_pool: List[str] = []
        self.locations: List[Dict] = []
        self.simulation_running = False
        self.simulation_progress = 0
        
        self._initialize_data_pools()
    
    def _initialize_data_pools(self):
        """Initialize pools of synthetic data for realistic simulation"""
        
        # Generate 10,000 device fingerprints
        self.device_pool = [
            self._generate_device_fingerprint() for _ in range(10000)
        ]
        
        # Generate 30 locations
        self.locations = [
            {"city": "Lagos", "country": "Nigeria", "lat": 6.5244, "lon": 3.3792, "timezone": "Africa/Lagos"},
            {"city": "Cairo", "country": "Egypt", "lat": 30.0444, "lon": 31.2357, "timezone": "Africa/Cairo"},
            {"city": "Kinshasa", "country": "DRC", "lat": -4.4419, "lon": 15.2663, "timezone": "Africa/Kinshasa"},
            {"city": "Johannesburg", "country": "South Africa", "lat": -26.2041, "lon": 28.0473, "timezone": "Africa/Johannesburg"},
            {"city": "Nairobi", "country": "Kenya", "lat": -1.2921, "lon": 36.8219, "timezone": "Africa/Nairobi"},
            {"city": "Casablanca", "country": "Morocco", "lat": 33.5731, "lon": -7.5898, "timezone": "Africa/Casablanca"},
            {"city": "Addis Ababa", "country": "Ethiopia", "lat": 9.1450, "lon": 40.4897, "timezone": "Africa/Addis_Ababa"},
            {"city": "Dar es Salaam", "country": "Tanzania", "lat": -6.7924, "lon": 39.2083, "timezone": "Africa/Dar_es_Salaam"},
            {"city": "Accra", "country": "Ghana", "lat": 5.6037, "lon": -0.1870, "timezone": "Africa/Accra"},
            {"city": "Abidjan", "country": "Ivory Coast", "lat": 5.3600, "lon": -4.0083, "timezone": "Africa/Abidjan"},
            {"city": "New York", "country": "US", "lat": 40.7128, "lon": -74.0060, "timezone": "America/New_York"},
            {"city": "London", "country": "UK", "lat": 51.5074, "lon": -0.1278, "timezone": "Europe/London"},
            {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lon": 139.6503, "timezone": "Asia/Tokyo"},
            {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lon": 151.2093, "timezone": "Australia/Sydney"},
            {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lon": 13.4050, "timezone": "Europe/Berlin"},
            {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lon": 103.8198, "timezone": "Asia/Singapore"},
            {"city": "Dubai", "country": "UAE", "lat": 25.2048, "lon": 55.2708, "timezone": "Asia/Dubai"},
            {"city": "São Paulo", "country": "Brazil", "lat": -23.5505, "lon": -46.6333, "timezone": "America/Sao_Paulo"},
            {"city": "Mumbai", "country": "India", "lat": 19.0760, "lon": 72.8777, "timezone": "Asia/Kolkata"},
            {"city": "Mexico City", "country": "Mexico", "lat": 19.4326, "lon": -99.1332, "timezone": "America/Mexico_City"},
            {"city": "Moscow", "country": "Russia", "lat": 55.7558, "lon": 37.6176, "timezone": "Europe/Moscow"},
            {"city": "Paris", "country": "France", "lat": 48.8566, "lon": 2.3522, "timezone": "Europe/Paris"},
            {"city": "Bangkok", "country": "Thailand", "lat": 13.7563, "lon": 100.5018, "timezone": "Asia/Bangkok"},
            {"city": "Seoul", "country": "South Korea", "lat": 37.5665, "lon": 126.9780, "timezone": "Asia/Seoul"},
            {"city": "Jakarta", "country": "Indonesia", "lat": -6.2088, "lon": 106.8456, "timezone": "Asia/Jakarta"},
            {"city": "Istanbul", "country": "Turkey", "lat": 41.0082, "lon": 28.9784, "timezone": "Europe/Istanbul"},
            {"city": "Buenos Aires", "country": "Argentina", "lat": -34.6118, "lon": -58.3960, "timezone": "America/Argentina/Buenos_Aires"},
            {"city": "Toronto", "country": "Canada", "lat": 43.6532, "lon": -79.3832, "timezone": "America/Toronto"},
            {"city": "Hong Kong", "country": "Hong Kong", "lat": 22.3193, "lon": 114.1694, "timezone": "Asia/Hong_Kong"},
            {"city": "Madrid", "country": "Spain", "lat": 40.4168, "lon": -3.7038, "timezone": "Europe/Madrid"},
        ]
                
        # Generate merchant pool
        merchant_categories = [
            "grocery", "gas_station", "restaurant", "retail", "online", 
            "pharmacy", "hotel", "airline", "entertainment", "subscription",
            "utility", "electronics", "jewelry", "automotive", "healthcare", 
            "education", "transport", "banking", "insurance", "real_estate", "beauty",
        ]
        
        for i in range(1000):
            merchant_id = f"merchant_{i:04d}"
            location = random.choice(self.locations)
            
            # Mobile money agents more common in African cities
            if location["country"] in ["Ghana", "Kenya", "Tanzania", "Uganda", "Rwanda", "Ivory Coast", "Ethiopia", "Nigeria"]:
                category = random.choice(merchant_categories + ["mobile_money_agent"] * 5)
            else:
                category = random.choice(merchant_categories)
            
            self.merchants[merchant_id] = {
                "name": self.faker.company(),
                "category": category,
                "risk_level": random.choice(["low", "medium", "high"]),
                "location": location
            }
    
    def _generate_device_fingerprint(self) -> str:
        """Generate a realistic device fingerprint"""
        browsers = ["Chrome", "Firefox", "Safari", "Edge", "Opera", "UC Browser", "Samsung Internet"]
        os_list = ["Windows", "MacOS", "Linux", "iOS", "Android", "KaiOS", "Ubuntu Touch"]
        
        return f"{random.choice(browsers)}_{random.choice(os_list)}_{uuid.uuid4().hex[:8]}"
    
    def _get_payment_methods_for_location(self, location: Dict) -> List[str]:
        """Get appropriate payment methods based on location"""
        base_methods = ["credit_card", "debit_card", "digital_wallet"]
        
        # Add bank transfer & mobile money for African countries
        if location["country"] in ["Nigeria", "Kenya", "Ghana", "Tanzania", "Uganda", "Rwanda", "Ivory Coast", "Ethiopia", "South Africa"]:
            return base_methods + ["mobile_money", "bank_transfer"]
        
        return base_methods
    
    def _generate_user(self) -> Dict[str, Any]:
        """Generate a synthetic user profile"""
        user_id = str(uuid.uuid4())
        home_location = random.choice(self.locations)
        
        user = {
            "user_id": user_id,
            "name": self.faker.name(),
            "email": self.faker.email(),
            "phone": self.faker.phone_number(),
            "home_location": home_location,
            "account_age_days": random.randint(30, 1095),
            "average_transaction_amount": random.uniform(10, 1000),
            "preferred_merchants": random.sample(list(self.merchants.keys()), k=random.randint(5, 20)),
            "risk_profile": random.choice(["low", "medium", "high"]),
            "devices": random.sample(self.device_pool, k=random.randint(1, 5)),
            "preferred_payment_methods": self._get_payment_methods_for_location(home_location)
        }
        
        self.users[user_id] = user
        return user
    
    def generate_normal_transaction(self, user_id: str) -> Transaction:
        """Generate a non-fraudulent transaction"""
        user = self.users[user_id]
        
        merchant_id = random.choice(user["preferred_merchants"])
        device = random.choice(user["devices"])
        
        amount = np.random.normal(user["average_transaction_amount"], 
                                user["average_transaction_amount"] * 0.3)
        amount = max(1.0, round(amount, 2))
        
        # Location is usually near home location, but can vary
        if random.random() < 0.8:
            location = user["home_location"]
        else:
            location = random.choice(self.locations)
        
        # Choose appropriate payment method
        payment_method = random.choice(user["preferred_payment_methods"])
        
        return Transaction(
            transaction_id=str(uuid.uuid4()),
            user_id=user_id,
            amount=amount,
            currency=random.choice(["USD", "EUR", "GBP", "NGN", "KES", "GHS", "ZAR"]),
            merchant_id=merchant_id,
            merchant_category=self.merchants[merchant_id]["category"],
            timestamp=datetime.utcnow().isoformat(),
            device_fingerprint=device,
            ip_address=self.faker.ipv4(),
            location=location,
            payment_method=payment_method,
            fraud_pattern=None,
            risk_score=random.uniform(0.1, 0.3)
        )
    
    def generate_rapid_fire_attack(self, user_id: str, count: int = 10) -> List[Transaction]:
        """Simulate rapid-fire low-value purchases"""
        transactions = []
        user = self.users[user_id]
        device = random.choice(user["devices"])
        base_time = datetime.utcnow()
        
        for i in range(count):
            amount = random.uniform(1.0, 15.0)
            timestamp = base_time + timedelta(seconds=i * random.randint(1, 5))
            
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                user_id=user_id,
                amount=amount,
                currency="USD",
                merchant_id=random.choice(list(self.merchants.keys())),
                merchant_category=random.choice(["online", "retail", "grocery"]),
                timestamp=timestamp.isoformat(),
                device_fingerprint=device,
                ip_address=self.faker.ipv4(),
                location=user["home_location"],
                payment_method=random.choice(user["preferred_payment_methods"]),
                fraud_pattern=FraudPattern.RAPID_FIRE.value,
                risk_score=random.uniform(0.7, 0.9)
            )
            transactions.append(transaction)
        
        return transactions
    
    def generate_geographic_hopping(self, user_id: str, count: int = 5) -> List[Transaction]:
        """Simulate impossible travel patterns"""
        transactions = []
        user = self.users[user_id]
        device = random.choice(user["devices"])
        base_time = datetime.utcnow()
        
        locations = random.sample(self.locations, min(count, len(self.locations)))
        
        for i, location in enumerate(locations):
            timestamp = base_time + timedelta(minutes=i * random.randint(5, 30))
            
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                user_id=user_id,
                amount=random.uniform(50, 500),
                currency="USD",
                merchant_id=random.choice(list(self.merchants.keys())),
                merchant_category=random.choice(["hotel", "restaurant", "gas_station"]),
                timestamp=timestamp.isoformat(),
                device_fingerprint=device,
                ip_address=self.faker.ipv4(),
                location=location,
                payment_method=random.choice(user["preferred_payment_methods"]),
                fraud_pattern=FraudPattern.GEOGRAPHIC_HOPPING.value,
                risk_score=random.uniform(0.8, 0.95)
            )
            transactions.append(transaction)
        
        return transactions
    
    def generate_device_spoofing(self, user_id: str, count: int = 8) -> List[Transaction]:
        """Simulate device fingerprint manipulation"""
        transactions = []
        user = self.users[user_id]
        base_time = datetime.utcnow()
        
        for i in range(count):
            device = self._generate_device_fingerprint()
            timestamp = base_time + timedelta(minutes=i * random.randint(10, 60))
            
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                user_id=user_id,
                amount=random.uniform(100, 1000),
                currency="USD",
                merchant_id=random.choice(list(self.merchants.keys())),
                merchant_category=random.choice(["online", "retail", "electronics"]),
                timestamp=timestamp.isoformat(),
                device_fingerprint=device,
                ip_address=self.faker.ipv4(),
                location=random.choice(self.locations),
                payment_method=random.choice(user["preferred_payment_methods"]),
                fraud_pattern=FraudPattern.DEVICE_SPOOFING.value,
                risk_score=random.uniform(0.6, 0.85)
            )
            transactions.append(transaction)
        
        return transactions
    
    def generate_amount_escalation(self, user_id: str, count: int = 6) -> List[Transaction]:
        """Simulate gradual amount escalation to test limits"""
        transactions = []
        user = self.users[user_id]
        device = random.choice(user["devices"])
        base_time = datetime.utcnow()
        
        base_amount = user["average_transaction_amount"]
        
        for i in range(count):
            multiplier = 1.5 ** i
            amount = base_amount * multiplier
            timestamp = base_time + timedelta(hours=i * random.randint(1, 6))
            
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                user_id=user_id,
                amount=round(amount, 2),
                currency="USD",
                merchant_id=random.choice(list(self.merchants.keys())),
                merchant_category=random.choice(["retail", "electronics", "luxury"]),
                timestamp=timestamp.isoformat(),
                device_fingerprint=device,
                ip_address=self.faker.ipv4(),
                location=user["home_location"],
                payment_method=random.choice(user["preferred_payment_methods"]),
                fraud_pattern=FraudPattern.AMOUNT_ESCALATION.value,
                risk_score=min(0.95, 0.4 + (i * 0.1))
            )
            transactions.append(transaction)
        
        return transactions
    
    def generate_merchant_cycling(self, user_id: str, count: int = 12) -> List[Transaction]:
        """Simulate cycling through many merchants quickly"""
        transactions = []
        user = self.users[user_id]
        device = random.choice(user["devices"])
        base_time = datetime.utcnow()
        
        # Use different merchants each time
        merchants = random.sample(list(self.merchants.keys()), min(count, len(self.merchants)))
        
        for i, merchant_id in enumerate(merchants):
            timestamp = base_time + timedelta(minutes=i * random.randint(2, 8))
            
            transaction = Transaction(
                transaction_id=str(uuid.uuid4()),
                user_id=user_id,
                amount=random.uniform(20, 200),
                currency="USD",
                merchant_id=merchant_id,
                merchant_category=self.merchants[merchant_id]["category"],
                timestamp=timestamp.isoformat(),
                device_fingerprint=device,
                ip_address=self.faker.ipv4(),
                location=user["home_location"],
                payment_method=random.choice(user["preferred_payment_methods"]),
                fraud_pattern=FraudPattern.MERCHANT_CYCLING.value,
                risk_score=random.uniform(0.5, 0.8)
            )
            transactions.append(transaction)
        
        return transactions
    
    def run_simulation(self, duration_hours: int = 24, transactions_per_hour: int = 100, 
                      fraud_patterns: List[str] = None, fraud_rate: float = 0.15,
                      progress_callback=None):
        """Run the main simulation with progress tracking"""
        logger.info(f"Starting simulation for {duration_hours} hours")
        
        self.simulation_running = True
        self.simulation_progress = 0
        self.transactions = []  # Reset transactions
        
        # Generate users
        num_users = max(50, transactions_per_hour // 10)
        self.users = {}  # Reset users
        for _ in range(num_users):
            self._generate_user()
        
        user_ids = list(self.users.keys())
        
        if fraud_patterns is None:
            fraud_patterns = [pattern.value for pattern in FraudPattern]
        
        total_transactions = duration_hours * transactions_per_hour
        
        for hour in range(duration_hours):
            if not self.simulation_running:
                break
                
            logger.info(f"Simulating hour {hour + 1}/{duration_hours}")
            
            for transaction_idx in range(transactions_per_hour):
                if not self.simulation_running:
                    break
                    
                user_id = random.choice(user_ids)
                
                if random.random() < fraud_rate:
                    # Generate fraudulent transaction
                    if FraudPattern.MIXED_PATTERNS.value in fraud_patterns:
                        pattern = random.choice([p for p in FraudPattern if p != FraudPattern.MIXED_PATTERNS])
                    else:
                        pattern = random.choice([FraudPattern(p) for p in fraud_patterns])
                    
                    if pattern == FraudPattern.RAPID_FIRE:
                        fraud_transactions = self.generate_rapid_fire_attack(user_id, count=random.randint(5, 15))
                    elif pattern == FraudPattern.GEOGRAPHIC_HOPPING:
                        fraud_transactions = self.generate_geographic_hopping(user_id, count=random.randint(3, 7))
                    elif pattern == FraudPattern.DEVICE_SPOOFING:
                        fraud_transactions = self.generate_device_spoofing(user_id, count=random.randint(4, 10))
                    elif pattern == FraudPattern.AMOUNT_ESCALATION:
                        fraud_transactions = self.generate_amount_escalation(user_id, count=random.randint(4, 8))
                    elif pattern == FraudPattern.MERCHANT_CYCLING:
                        fraud_transactions = self.generate_merchant_cycling(user_id, count=random.randint(6, 12))
                    else:
                        fraud_transactions = self.generate_rapid_fire_attack(user_id, count=random.randint(5, 15))
                    
                    self.transactions.extend(fraud_transactions)
                else:
                    # Generate normal transaction
                    transaction = self.generate_normal_transaction(user_id)
                    self.transactions.append(transaction)
                
                # Update progress
                current_progress = ((hour * transactions_per_hour) + transaction_idx + 1) / total_transactions * 100
                self.simulation_progress = min(current_progress, 100)
                
                if progress_callback:
                    progress_callback(self.simulation_progress)
                
                # Small delay to allow for interruption
                time.sleep(0.002)
        
        self.simulation_running = False
        self.simulation_progress = 100
        logger.info("Simulation completed")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive simulation report"""
        if not self.transactions:
            return {"error": "No transactions to report"}
        
        total_transactions = len(self.transactions)
        fraudulent_transactions = [t for t in self.transactions if t.fraud_pattern]
        normal_transactions = [t for t in self.transactions if not t.fraud_pattern]
        
        # Pattern analysis
        pattern_counts = {}
        pattern_amounts = {}
        for transaction in fraudulent_transactions:
            pattern = transaction.fraud_pattern
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
            pattern_amounts[pattern] = pattern_amounts.get(pattern, 0) + transaction.amount
        
        # Location analysis
        location_stats = {}
        for transaction in self.transactions:
            location = transaction.location["city"]
            if location not in location_stats:
                location_stats[location] = {"total": 0, "fraud": 0, "amount": 0}
            location_stats[location]["total"] += 1
            location_stats[location]["amount"] += transaction.amount
            if transaction.fraud_pattern:
                location_stats[location]["fraud"] += 1
        
        # Payment method analysis
        payment_method_stats = {}
        for transaction in self.transactions:
            method = transaction.payment_method
            if method not in payment_method_stats:
                payment_method_stats[method] = {"total": 0, "fraud": 0, "amount": 0}
            payment_method_stats[method]["total"] += 1
            payment_method_stats[method]["amount"] += transaction.amount
            if transaction.fraud_pattern:
                payment_method_stats[method]["fraud"] += 1
        
        # Risk score analysis
        risk_scores = [t.risk_score for t in self.transactions if t.risk_score]
        avg_risk_score = sum(risk_scores) / len(risk_scores) if risk_scores else 0
        
        total_amount = sum(t.amount for t in self.transactions)
        fraud_amount = sum(t.amount for t in fraudulent_transactions)
        
        return {
            "summary": {
                "total_transactions": total_transactions,
                "fraudulent_transactions": len(fraudulent_transactions),
                "normal_transactions": len(normal_transactions),
                "fraud_rate": len(fraudulent_transactions) / total_transactions if total_transactions > 0 else 0,
                "total_amount": round(total_amount, 2),
                "fraud_amount": round(fraud_amount, 2),
                "fraud_amount_percentage": (fraud_amount / total_amount) * 100 if total_amount > 0 else 0,
                "average_risk_score": round(avg_risk_score, 3),
                "unique_users": len(self.users),
                "unique_merchants": len(set(t.merchant_id for t in self.transactions)),
                "unique_devices": len(set(t.device_fingerprint for t in self.transactions)),
                "unique_locations": len(set(t.location["city"] for t in self.transactions))
            },
            "pattern_analysis": {
                "counts": pattern_counts,
                "amounts": {k: round(v, 2) for k, v in pattern_amounts.items()}
            },
            "location_analysis": {
                k: {
                    "total_transactions": v["total"],
                    "fraud_transactions": v["fraud"],
                    "fraud_rate": v["fraud"] / v["total"] if v["total"] > 0 else 0,
                    "total_amount": round(v["amount"], 2)
                }
                for k, v in location_stats.items()
            },
            "payment_method_analysis": {
                k: {
                    "total_transactions": v["total"],
                    "fraud_transactions": v["fraud"],
                    "fraud_rate": v["fraud"] / v["total"] if v["total"] > 0 else 0,
                    "total_amount": round(v["amount"], 2)
                }
                for k, v in payment_method_stats.items()
            },
            "transactions": [asdict(t) for t in self.transactions[-100:]]  # Last 100 transactions
        }
    
    def stop_simulation(self):
        """Stop the running simulation"""
        self.simulation_running = False

# Global simulator instance
simulator = SyntheticFraudSimulator()

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    """Start simulation with parameters"""
    try:
        data = request.json
        duration_hours = int(data.get('duration_hours', 1))
        transactions_per_hour = int(data.get('transactions_per_hour', 100))
        fraud_patterns = data.get('fraud_patterns', [])
        fraud_rate = float(data.get('fraud_rate', 0.15))
        
        if simulator.simulation_running:
            return jsonify({"error": "Simulation already running"}), 400
        
        # Run simulation in background thread
        def run_sim():
            simulator.run_simulation(
                duration_hours=duration_hours,
                transactions_per_hour=transactions_per_hour,
                fraud_patterns=fraud_patterns,
                fraud_rate=fraud_rate
            )
        
        thread = threading.Thread(target=run_sim)
        thread.daemon = True
        thread.start()
        
        return jsonify({"message": "Simulation started", "status": "running"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/simulation_status')
def simulation_status():
    """Get current simulation status"""
    return jsonify({
        "running": simulator.simulation_running,
        "progress": simulator.simulation_progress,
        "total_transactions": len(simulator.transactions)
    })

@app.route('/stop_simulation', methods=['POST'])
def stop_simulation():
    """Stop the running simulation"""
    simulator.stop_simulation()
    return jsonify({"message": "Simulation stopped"})

@app.route('/get_report')
def get_report():
    """Get simulation report"""
    try:
        report = simulator.generate_report()
        return jsonify(report)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear_data', methods=['POST'])
def clear_data():
    """Clear all simulation data"""
    simulator.transactions = []
    simulator.users = {}
    simulator.simulation_progress = 0
    return jsonify({"message": "Data cleared"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)