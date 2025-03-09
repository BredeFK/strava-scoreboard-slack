class Athlete:
    def __init__(self, name, total_distance=0, num_activities=0, total_moving_time=0, longest_activity=0, total_elevation_gain=0):
        self.name = name
        self.total_distance = total_distance
        self.num_activities = num_activities
        self.total_moving_time = total_moving_time
        self.longest_activity = longest_activity
        self.total_elevation_gain = total_elevation_gain

    def add_activity(self, distance, moving_time, elevation_gain):
        self.total_distance += distance
        self.num_activities += 1
        self.total_moving_time += moving_time
        self.longest_activity = max(self.longest_activity, distance)
        self.total_elevation_gain += elevation_gain

    def avg_pace_per_km(self):
        if self.total_distance == 0:
            return None
        pace_seconds = self.total_moving_time / (self.total_distance / 1000)
        minutes = int(pace_seconds // 60)
        seconds = int(pace_seconds % 60)
        return f"{minutes}:{seconds:02d} /km"

    def get_total_distance(self):
        return f'{self.total_distance / 1000:.2f} km'

    def get_longest_activity(self):
        return f'{self.longest_activity / 1000:.2f} km'

    def get_total_elevation_gain(self):
        if self.total_elevation_gain == 0:
            return '--'
        else:
            return f'{int(self.total_elevation_gain)} m'

    def __repr__(self):
        return (f"{self.name}: {self.get_total_distance()}, "
                f"{self.num_activities} activities, "
                f"Pace {self.avg_pace_per_km()}, "
                f"Longest: {self.get_longest_activity()}, "
                f"Climbed: {self.get_total_elevation_gain()}")
