#include "mastermind.h"

#include <ctype.h>
#include <stdio.h>
#include <string.h>

#define ANSI_RESET  "\033[0m"
#define ANSI_RED    "\033[31m"
#define ANSI_GREEN  "\033[32m"
#define ANSI_YELLOW "\033[33m"

void
game_init_board(struct board_state *b, enum player_role role)
{
  memset(b, 0, sizeof(*b));
  b->role = role;
  snprintf(b->master_seq, sizeof(b->master_seq), "*****");
  b->master_seq_known = (role == ROLE_MASTERMIND);
}

bool
game_validate_sequence(const char *seq)
{
  if (seq == nullptr || strlen(seq) != MM_SEQ_LEN) {
    return false;
  }
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (seq[i] < '0' || seq[i] > '9') {
      return false;
    }
  }
  return true;
}

bool
game_validate_feedback(const char *fb)
{
  if (fb == nullptr || strlen(fb) != MM_SEQ_LEN) {
    return false;
  }
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (fb[i] != 'x' && fb[i] != 'o' && fb[i] != '-') {
      return false;
    }
  }
  return true;
}

void
game_compute_expected_feedback(const char *master_seq, const char *guess,
                               char out_fb[MM_SEQ_LEN + 1])
{
  bool master_used[MM_SEQ_LEN] = {false};

  /* First pass: exact position matches ('x') */
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (guess[i] == master_seq[i]) {
      out_fb[i] = 'x';
      master_used[i] = true;
    } else {
      out_fb[i] = '-';
    }
  }

  /* Second pass: right digit in wrong position ('o') */
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (out_fb[i] == 'x') {
      continue;
    }
    for (int j = 0; j < MM_SEQ_LEN; j++) {
      if (!master_used[j] && guess[i] == master_seq[j]) {
        out_fb[i] = 'o';
        master_used[j] = true;
        break;
      }
    }
  }
  out_fb[MM_SEQ_LEN] = '\0';
}

static void
print_colored_guess(const char *guess, const char *fb, bool has_fb,
                    enum player_role role)
{
  for (int i = 0; i < MM_SEQ_LEN; i++) {
    if (role == ROLE_CODEBREAKER && has_fb) {
      const char *color = ANSI_RED;
      if (fb[i] == 'x') {
        color = ANSI_GREEN;
      } else if (fb[i] == 'o') {
        color = ANSI_YELLOW;
      }
      printf("%s%c%s ", color, guess[i], ANSI_RESET);
    } else {
      printf("%c ", guess[i]);
    }
  }
}

void
game_render_board(const struct board_state *b, const char *opponent_name,
                  const char *status_line)
{
  printf("\033[2J\033[H");
  printf("====================================================\n");
  printf("  MASTERMIND vs. %s (%s)\n", opponent_name,
         b->role == ROLE_MASTERMIND ? "You are Mastermind"
                                    : "You are Codebreaker");
  printf("====================================================\n");

  printf("  Master Sequence: ");
  if (b->master_seq_known) {
    for (int i = 0; i < MM_SEQ_LEN; i++) {
      printf("%c ", b->master_seq[i]);
    }
  } else {
    printf("* * * * *");
  }
  printf("\n----------------------------------------------------\n");
  printf("  Turn  |   Attempt   |  Feedback\n");
  printf("----------------------------------------------------\n");

  for (int r = 0; r < MM_MAX_ATTEMPTS; r++) {
    printf("   %2d   |  ", r + 1);
    if (r < b->num_attempts) {
      print_colored_guess(b->guesses[r], b->feedbacks[r], b->feedback_ready[r],
                          b->role);
      printf(" |  ");
      if (b->feedback_ready[r]) {
        for (int i = 0; i < MM_SEQ_LEN; i++) {
          const char *color = ANSI_RED;
          if (b->feedbacks[r][i] == 'x') {
            color = ANSI_GREEN;
          } else if (b->feedbacks[r][i] == 'o') {
            color = ANSI_YELLOW;
          }
          printf("%s%c%s ", color, b->feedbacks[r][i], ANSI_RESET);
        }
      } else {
        printf(". . . . .");
      }
    } else {
      printf(". . . . .  |  . . . . .");
    }
    printf("\n");
  }

  printf("====================================================\n");
  if (status_line != nullptr && status_line[0] != '\0') {
    printf("%s", status_line);
    fflush(stdout);
  }
}
