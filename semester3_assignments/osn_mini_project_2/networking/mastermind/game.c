#include "mastermind.h"

#include <stdio.h>
#include <string.h>

/* ANSI color codes for codebreaker feedback ('x'=green, 'o'=yellow, '-'=red) */
#define COLOR_GREEN  "\033[32m"
#define COLOR_YELLOW "\033[33m"
#define COLOR_RED    "\033[31m"
#define COLOR_RESET  "\033[0m"

void
init_board(struct board_state *b, int role)
{
  memset(b, 0, sizeof(*b));
  b->role = role;
  strcpy(b->master_seq, "*****");
  if (role == ROLE_MASTERMIND) {
    b->show_master_seq = 1;
  } else {
    b->show_master_seq = 0;
  }
}

/* Sequence must be 5 characters and all digits '0' to '9' */
int
is_valid_sequence(const char *s)
{
  if (s == NULL || strlen(s) != MM_SEQ_LEN) {
    return 0;
  }
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (s[i] < '0' || s[i] > '9') {
      return 0;
    }
  }
  return 1;
}

/* Feedback must be 5 characters and only 'x', 'o', or '-' */
int
is_valid_feedback(const char *s)
{
  if (s == NULL || strlen(s) != MM_SEQ_LEN) {
    return 0;
  }
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (s[i] != 'x' && s[i] != 'o' && s[i] != '-') {
      return 0;
    }
  }
  return 1;
}

/* Calculate expected feedback pegs ('x' count, 'o' count, '-' count) */
void
calculate_feedback(const char *master_seq, const char *guess,
                   char out_fb[MM_SEQ_LEN + 1])
{
  int master_used[MM_SEQ_LEN] = {0, 0, 0, 0, 0};
  int guess_used[MM_SEQ_LEN] = {0, 0, 0, 0, 0};
  int x_count = 0;
  int o_count = 0;

  /* Pass 1: count exact digit + position matches ('x') */
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (guess[i] == master_seq[i]) {
      x_count++;
      master_used[i] = 1;
      guess_used[i] = 1;
    }
  }

  /* Pass 2: count right digit in wrong position ('o') */
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (guess_used[i]) {
      continue;
    }
    for (int j = 0; j < MM_SEQ_LEN; j++) {
      if (!master_used[j] && guess[i] == master_seq[j]) {
        o_count++;
        master_used[j] = 1;
        break;
      }
    }
  }

  int pos = 0;
  for (int i = 0; i < x_count; i++) {
    out_fb[pos++] = 'x';
  }
  for (int i = 0; i < o_count; i++) {
    out_fb[pos++] = 'o';
  }
  while (pos < MM_SEQ_LEN) {
    out_fb[pos++] = '-';
  }
  out_fb[MM_SEQ_LEN] = '\0';
}

/* Print the 12-row Mastermind board in the exact format from the assignment spec */
void
print_board(const struct board_state *b)
{
  printf("\033[2J\033[H");

  for (int r = 0; r < MM_MAX_ATTEMPTS; r++) {
    if (r < b->num_attempts) {
      printf("%s  ", b->guesses[r]);
      if (b->has_feedback[r]) {
        for (int i = 0; i < MM_SEQ_LEN; i++) {
          char c = b->feedbacks[r][i];
          if (b->role == ROLE_CODEBREAKER) {
            if (c == 'x') {
              printf("%s%c%s", COLOR_GREEN, c, COLOR_RESET);
            } else if (c == 'o') {
              printf("%s%c%s", COLOR_YELLOW, c, COLOR_RESET);
            } else {
              printf("%s%c%s", COLOR_RED, c, COLOR_RESET);
            }
          } else {
            printf("%c", c);
          }
        }
        printf("\n");
      } else {
        printf("*****\n");
      }
    } else {
      printf("*****  *****\n");
    }
  }

  printf("-----\n");
  if (b->show_master_seq) {
    printf("%s\n", b->master_seq);
  } else {
    printf("*****\n");
  }
  fflush(stdout);
}
