from rapidfuzz import fuzz


def quote_search(quote: str, chunks: list[str]):
    scores = []

    for chunk in chunks:
        score = fuzz.partial_ratio(quote, chunk)
        scores.append(score)
        print(score)
    print(scores)
    max_score = max(scores)
    best_index = scores.index(max_score)
    best_match = chunks[best_index]
    print(best_match)
    return best_index, max_score


quote = "it was not until my senior season that my sleep habits, study habits, and strength-training habits really began to pay off"

chunks = [
    "order. While my peers stayed up late and played video games, I built good sleep habits and went to bed early each night. In the messy world of a college dorm, I made a point to keep my room neat and tidy. These improvements were minor, but they gave me a sense of control over my life. I started to feel confident again. And this growing belief in myself rippled into the classroom as I improved my study habits and managed to earn straight A\u2019s during my first year, A habit is a routine or behavior that is performed regularly\u2014and, in many cases, automatically. As each semester passed, I accumulated small but consistent habits that ultimately led to results that were unimaginable to me when I started. For example, for the first time in my life, I made it a habit to lift weights multiple times per week, and in the years that followed, my six-foot-four-inch frame bulked up from a featherweight 170 to a lean 200 pounds. When my sophomore season arrived, I earned a starting role on the pitching staff. By my junior year, I was voted team captain and at the end of the season, I was",
    "concepts in this book can help you fulfill your potential as well. We all face challenges in life. This injury was one of mine, and the experience taught me a critical lesson: changes that seem small and unimportant at first will compound into remarkable results if you\u2019re willing to stick with them for years. We all deal with setbacks but in the long run, the quality of our lives often depends on the quality of our habits. With the same habits, you\u2019ll end up with the same results. But with better habits, anything is possible. Maybe there are people who can achieve incredible success overnight. I don\u2019t know any of them, and I\u2019m certainly not one of them. There wasn\u2019t one defining moment on my journey from medically induced coma to Academic All-American; there were many. It was a gradual evolution, a long series of small wins and tiny breakthroughs. The only way I made progress\u2014the only choice I had\u2014was to start small. And I employed this same strategy a few years later when I started my own business and began working on this book. HOW AND WHY I WROTE THIS BOOK In November 2012 ,1 began publishing articles atjamesclear.com.",
    "pitching staff. By my junior year, I was voted team captain and at the end of the season, I was selected for the all-conference team. But it was not until my senior season that my sleep habits, study habits, and strength-training habits really began to pay off. Six years after I had been hit in the face with a baseball bat, flown to the hospital, and placed into a coma, I was selected as the top male athlete at Denison University and named to the ESPN Academic All- America Team\u2014an honor given to just thirty-three players across the country. By the time I graduated, I was listed in the school record books in eight different categories. That same year, I was awarded the university\u2019s highest academic honor, the President\u2019s Medal, I hope you\u2019ll forgive me if this sounds boastful. To be honest, there was nothing legendary or historic about my athletic career. I never ended up playing professionally. However, looking back on those years, I believe I accomplished something just as rare: I fulfilled my potential. And I believe the concepts in this book can help you fulfill your potential as well. We all face challenges in life. This injury",
]

quote_search(quote, chunks)
