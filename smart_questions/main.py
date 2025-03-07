# ```sql
# SELECT fio from teachers
# WHERE id IN (
#     SELECT teacher_id FROM participants
#     WHERE
#         result < 4
#         AND teacher_id NOT IN (
#             SELECT teacher_id FROM participants WHERE result > 3)
# );
# ```

