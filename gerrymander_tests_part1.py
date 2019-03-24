# #####second case is when you have an actual year and state of interest. That's what I'll be focusing on getting
# working first (the case when year != 0).
#
# To test run this function, use: gerrymander_tests_part1(2012,38,2012,0,0.75,0,'Pennsylvania','foo')
# p1 of the Matlab code is the probability, and it's the main thing that's being calculated

from datetime import datetime
from statistics import mean
import numpy as np
from scipy import stats
from scipy.stats import norm
import pandas as pd
import matplotlib.pyplot as plt


######################################################################################################################

def gerrymander_read_results(year, states):
    # Let's read the csv file into a pandas data frame
    df = pd.read_csv('House_1898_2014_voteshares_notext.csv', header=None)
    # Let's name the columns
    df.columns = ['Year', 'State', 'District', 'D_voteshare', 'Incumbent', 'Winner']
    # We'll only extract those with the correct year
    year_df = df[df['Year'] == year]
    # Now we'll just take the values with the correct states
    result = year_df[year_df['State'].isin(states)]
    # Drop the 'Year' column from the data frame
    del result['Year']
    # Return the remaining data frame
    return result


# This is a port of gerrymander_state_name.m
def gerrymander_state_name(state_number_list):
    """This function accepts a list of ints as an input and returns the state
    abbreviations corresponding to those numbers"""
    state_list = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA',
                  'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NV', 'NH', 'NJ', 'NM',
                  'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA',
                  'WA', 'WV', 'WI', 'WY']
    print_list = [state_number for state_number in state_number_list if 0 < state_number < 51]
    for i in range(len(print_list)):
        return state_list[print_list[i] - 1]


def indices(a, func):
    return [i for (i, val) in enumerate(a) if func(val)]


def int_to_list(possible_int):
    """This function converts an int to a list of ints with size = 1. If the input is already a list it returns it as
    is """
    if type(possible_int) == int:
        possible_int = [possible_int]
    return possible_int


def var_test(data_c, var_c):
    """This function calculates variance test like the similar function in Matlab in source code with left tail"""
    df = len(data_c) - 1
    var_d = np.var(data_c, ddof=1)
    x2 = df * var_d / var_c
    p2b = stats.chi2.cdf(x2, df)
    return p2b


######################################################################################################################


def gerrymander_tests_part1(year, states, year_baseline, state_baseline, imputed_uncontested, symm, state_label,
                            output_filename):
    # Check to make sure states and state_baseline are lists of ints
    states = int_to_list(states)
    state_baseline = int_to_list(state_baseline)

    election_message = 'Election to be analyzed: '

    parameter_list0 = 'Parameters: year=%s ' % year
    if year == 0:
        parameter_list1 = 'states=%s ' % len(states)  # need to check!!!!
        parameter_list1 = parameter_list1 + ' year_baseline=%i state_baseline=' % year_baseline
    else:
        parameter_list1 = 'Parameters: year=%i states=%i year_baseline=%i state_baseline=' % (
            year, len(states), year_baseline)

    parameter_list2 = '%i ' % len(state_baseline)
    parameter_list3 = 'imputed_uncontested=%.2f symm=%i state_label=%s output_filename=%s' % (
        imputed_uncontested, symm, state_label, output_filename)
    parameter_listing = parameter_list0 + parameter_list1 + parameter_list2 + parameter_list3

    # reset_selective parameter_list0 parameter_list1 parameter_list2 parameter_list3

    if year == 0:
        state_raw = ['D_voteshare']  # use the variable "states" as the voting results data
        election_message = election_message + 'Custom data set, ' + state_label
    elif year in np.arange(1898, 2100, 2):
        state_data = gerrymander_read_results(year, states)
        state_raw = state_data['D_voteshare']  # I'm thinking he's looking for D_voteshare
        state_name = [gerrymander_state_name(states)]
        election_message = election_message + ' U.S. House election of ' + str(year) + ' in ' + str(state_name)
    else:
        state_data = gerrymander_read_results(2012, 38)
        state_raw = state_data['D_voteshare']  # I'm thinking he's looking for D_voteshare
        # state_name = gerrymander_state_name([38])
        print("Year parameter didn't parse - defaulting to U.S. House Pennsylvania 2012")

    baseline_message = 'Districts to be sampled for fantasy delegations: '

    ##############################################################################
    national_data = gerrymander_read_results(year_baseline, state_baseline)

    if year_baseline == 0:
        len(national_data)
        foo = np.random.normal(0.5, 0.15, 435)  # generate a generic random distribution
        foo[foo < 0] = 0
        foo[foo > 1] = 1
        national_data['D_voteshare'] = foo  # ????? really national data isn't loaded !!!
        national_raw = foo
        baseline_message = baseline_message + ' Random, partisan-symmetric districts.'
    elif year_baseline in np.arange(1898, 2016, 2):
        baseline_message = baseline_message + ' U.S. House results of ' + str(year_baseline)
        if state_baseline[0] < 1:
            national_data = gerrymander_read_results(year_baseline, list(range(1, 51)))
            baseline_message = baseline_message + ' in all 50 states'
        else:
            national_data = gerrymander_read_results(year_baseline, state_baseline)
            if len(state_baseline) == 50:
                baseline_message = baseline_message + ' in all 50 states'
            elif len(state_baseline) >= 30:
                omit_states = np.setdiff1d(list(range(1, 51)), state_baseline)
                baseline_message = baseline_message + ' in all states, but omitting: ' + gerrymander_state_name(
                    omit_states)
            else:
                baseline_message = baseline_message + ' in: ' + str(gerrymander_state_name(state_baseline))

        national_raw = national_data['D_voteshare']
    else:  # just do Pennsylvania 2012 ???????? incorrect comment ????????
        # national_data = gerrymander_read_results(2012, list(range(1, 51)))
        baseline_message = baseline_message + ' U.S. House 2012'
        print("Year_baseline parameter didn't parse - defaulting national data to 2012")
        national_raw = national_data['D_voteshare']  # Added because referenced without assignment

    n_delegates = len(state_raw)
    d_districts = indices(state_raw, lambda x_temp: x_temp >= 0.5)
    r_districts = indices(state_raw, lambda x_temp2: x_temp2 < 0.5)
    n__d = len(d_districts)
    n__r = n_delegates - n__d

    # Let's round state_raw to 5 digits to for the 1.00000's to 1
    rounded_state_raw = [round(state, 5) for state in state_raw]
    any_imputed = 0 in rounded_state_raw or 1 in rounded_state_raw
    imputed_uncontested = min(imputed_uncontested, 1)
    imputed_uncontested = max(imputed_uncontested, 0)
    imputed_floor = min(imputed_uncontested, 1 - imputed_uncontested)

    state_results = state_raw
    # Turn all the 0's in state_results into whatever number the imputed floor is
    state_results[state_results == 0] = imputed_floor
    state_results[state_results == 1] = 1 - imputed_floor  # Setting value on a copy, gives a warning

    national_results = national_raw
    national_results[national_results == 0] = imputed_floor
    national_results[national_results == 1] = 1 - imputed_floor

    d_mean_raw = mean(state_raw)
    r_mean_raw = 1 - d_mean_raw  # Not currently used
    d_mean = mean(state_results)
    r_mean = 1 - d_mean

    f1 = open(output_filename + '.html', 'w')

    site = 'http://gerrymander.princeton.edu'
    msg = '<b>Gerrymandering analyzer from Prof. Sam Wang, Princeton University</b>'
    print("<p><a href = \"%s\">%s</a></p>\n<p></p>\n<p>" % (site, msg), file=f1)

    print('%s</p>\n<p>' % election_message, file=f1)
    print('%s</p>\n<p></p>\n<p>' % baseline_message, file=f1)
    state_name = gerrymander_state_name(states)  # will give two-letter abbreviation of state

    if n_delegates <= 1:
        format_spec = 'Analysis is not possible. %s only has one representative listed, and single-district states ' \
                      'cannot be redistricted.</p>\n '
        print(format_spec % state_name, file=f1)
    # results=0
    else:
        state_name = gerrymander_state_name(states)  # will give two-letter abbreviation of state  ?????????
        format_spec = 'The %s delegation has %i seats, %i Democratic/other and %i Republican.</p>\n<p>'
        print(format_spec % (str(state_name), n_delegates, n__d, n__r), file=f1)
        if imputed_uncontested != 0:
            print('Uncontested races are assumed to have been won with %i%% of the vote.</p>\n<p>' % (
                imputed_uncontested * 100), file=f1)

        print('The average Democratic share of the two-party total vote was %2.1f%% (raw)' % (d_mean_raw * 100),
              file=f1)
        if d_mean_raw != d_mean:
            print(', %2.1f%% with imputation of uncontested races' % (d_mean * 100), file=f1)

        print(".</p>\n<p></p>\n<p>", file=f1)

        print("<b>Analysis of Intents</b></p>\n<p></p>\n<p>", file=f1)

        print("If a political party wishes to create for itself an advantage, it will pack its opponents to win "
              "overwhelmingly in a small number of districts, while distributing its own votes more thinly, "
              "but still to produce reliable wins. ",
              file=f1)
        print('</p>\n<p></p>\n<p>', file=f1)
        print("Partisan gerrymandering arises not from single districts, but from patterns of outcomes. Thus a single "
              "lopsided district may not be an offense - indeed, single-district gerrymandering is permitted by "
              "Supreme Court precedent, and may be required for the construction of individual districts that comply "
              "with the Voting Rights Act. Rather, it is combinations of outcomes that confer undue advantage to one "
              "party or the other.",
              file=f1)
        print('</p>\n<p></p>\n<p>', file=f1)
        print('The following two tests provide a way of quantifying any such advantage in a set of election results.',
              file=f1)
        print('</p>\n<p></p>\n<p>', file=f1)

        #########################################
        ##### Test for lopsided win margins #####
        #########################################

        print('%s Test 1\n' % str(datetime.now()))
        print('<b>First Test of Intents: Probing for lopsided win margins (the two-sample t-test):</b> ', file=f1)
        print("To test for a lopsided advantage, one can compare each party's winning margins and see if they are "
              "systematically different. ", file=f1)
        print('This is done using the <a href="http://vassarstats.net/textbook/ch11pt1.html">two-sample t-test</a>. ',
              file=f1)
        print('In this test, the party with the <i>smaller</i> set of winning margins has the '
              'advantage.</p>\n<p></p>\n<p>', file=f1)

        if n__d >= 2 and n__r >= 2:
            # calculate 2-sided t-test:
            [t1, p1] = stats.ttest_ind(list(state_results.tolist()[i] for i in d_districts),
                                       list(1 - state_results.tolist()[i] for i in r_districts), equal_var=True)
            # one side of the t test: there are two possibilities:
            # the mean sample 1 is > mean sample 2,  we want P/2 < P_critical, t>0
            # mean sample 1 is < mean sample 2, we want P/2< P_critical, t<0
            p1 = p1 / 2
            if mean(state_results.tolist()[i] for i in d_districts) > mean(
                            1 - state_results.tolist()[i] for i in r_districts):
                if t1 < 0:
                    # save the NULL hypothesis
                    p1 = p1 + 1
            else:
                if t1 > 0:
                    # save the NULL hypothesis
                    p1 = p1 + 1

            if p1 > 0.05:
                print('The difference between the two parties win margins does not meet established standards for '
                      'statistical significance. ',
                      file=f1)
                print('The probability that this difference or larger could have arisen by partisan-unbiased '
                      'mechanisms is %1.2f.' % p1,
                      file=f1)
            else:
                print('The difference between the two parties win margins meets established standards for statistical '
                      'significance. ',
                      file=f1)
                if p1 >= 0.01:
                    print('The probability that this difference in win margins (or larger) would have arisen by '
                          'partisan-unbiased mechanisms alone is %1.2f. ' % p1,
                          file=f1)
                else:
                    if p1 >= 0.001:
                        print('The probability that this difference in win margins (or larger) would have arisen by '
                              'partisan-unbiased mechanisms alone is %1.3f. ' % p1,
                              file=f1)
                    else:
                        print('The probability that this difference in win margins (or larger) would have arisen by '
                              'partisan-unbiased mechanisms alone is less than 0.001. ',
                              file=f1)

            print('</p>\n<p></p>\n<p>', file=f1)

            df_state_raw = state_raw.to_frame()
            df_state_raw['pol'] = np.where(df_state_raw['D_voteshare'] >= 0.5, 'Democratic', 'Republican')
            df_state_raw['D_voteshare'] = np.where(df_state_raw['D_voteshare'] >= 0.5,
                                                   df_state_raw['D_voteshare'] * 100,
                                                   100 - df_state_raw['D_voteshare'] * 100)

            labels = ['Democratic', 'Republican']
            data_d = df_state_raw[df_state_raw.pol == 'Democratic']['D_voteshare']
            data_r = df_state_raw[df_state_raw.pol == 'Republican']['D_voteshare']
            data = [data_d, data_r]

            fig = plt.figure()
            fig.suptitle('Analysis of Intents: Lopsided wins by one side', fontsize=10, fontweight='bold')
            ax = fig.add_subplot(111)
            ax.boxplot(data, 0, 'ro', 0, labels=labels, showfliers=True, showmeans=True)
            ax.scatter(data_d, np.ones(len(data_d)))
            ax.scatter(data_r, 2 * np.ones(len(data_r)))
            ax.set_xlabel('Winning vote percentage')
            plt.savefig(output_filename + '_Test1.png')
            #           plt.show()
            print('<IMG SRC="%s_Test1.png" border="0" alt="Logo"></p>\n<p>' % output_filename, file=f1)
        else:
            print("Can't compare win margins. For this test, both parties must have at least two "
                  "seats.</p>\n<p></p>\n<p>", file=f1)

            #########################################
            ##### Test for asymmetric advantage #####
            #########################################
        print('%s Test 2\n' % str(datetime.now()))
        print("<b>Second Test of Intents: Probing for asymmetric advantage for one party (mean-median difference "
              "and/or chi-square test):</b> ", file=f1)
        print('The choice of test depends on whether the parties are closely matched (mean-median difference) or one '
              'party is dominant (chi-square test of variance).</p>\n<p></p>\n<p>',
              file=f1)

        partisan_balance = abs(mean(state_results) - 0.5)
        if partisan_balance < 0.06:
            print('When the parties are closely matched in overall strength, a partisan advantage will be evident in '
                  'the form of a difference between the mean (a.k.a. average) vote share and the median vote share, '
                  'calculated across all districts. </p>\n<p></p>\n<p>',
                  file=f1)
            # mean minus median test
            mean_median_diff = mean(state_results) - np.median(state_results)
            s_k_mmdiff = mean_median_diff / np.std(state_results, ddof=1) * np.sqrt(
                len(state_results) / 0.5708)  # the 0.5708 comes from p. 352 of Cabilio and Masaro 1996
            p_value_mmdiff = min(norm.cdf(s_k_mmdiff), 1 - norm.cdf(
                s_k_mmdiff))  # One-tailed p-value, usually appropriate since most testers have a direction in mind
            mean_median_diff_p = abs(mean_median_diff) * 100
            if mean_median_diff < 0:
                print("The mean-median difference is %2.1f %% in a direction of advantage to the Democratic Party. "
                      % mean_median_diff_p,
                      file=f1)
            elif mean_median_diff > 0:
                print("The mean-median difference is %2.1f %% in a direction of advantage to the Republican Party. "
                      % mean_median_diff_p,
                      file=f1)
            else:
                print('The mean and median are identical, suggesting no identifiable advantage to either major party. '
                      'This can occur in situations where all races are uncontested.', file=f1)

            p_value_mmdiff_p = p_value_mmdiff * 100
            print("The mean-median difference would reach this value in %2.1f %% of situations by a partisan-unbiased "
                  "process. " % p_value_mmdiff_p, file=f1)
            if p_value_mmdiff < 0.01:
                print("This difference is statistically significant (p<0.01), and in a case of suspected "
                      "gerrymandering is extremely unlikely to have arisen by chance. ", file=f1)
            elif p_value_mmdiff < 0.05:
                print("This difference is statistically significant (p<0.05), and in a case of suspected "
                      "gerrymandering is unlikely to have arisen by chance. ",
                      file=f1)
            else:
                print("This difference is not statistically significant (p>0.05). ", file=f1)
            print("</p>\n<p></p>\n<p>", file=f1)

            df_state_raw = state_raw.to_frame()
            df_state_raw['pol'] = np.where(df_state_raw['D_voteshare'] >= 0.5, 'Blue', 'Red')
            df_state_raw['D_voteshare'] = df_state_raw['D_voteshare'] * 100

            labels = state_name
            data = [df_state_raw['D_voteshare']]
            # color = list(df_state_raw['pol'])
            fig = plt.figure()
            fig.suptitle('Analysis of Intents: Mean-median difference in vote share', fontsize=10, fontweight='bold')
            ax = fig.add_subplot(111)
            ax.boxplot(data, 0, 'rs', 0, showmeans=True) # labels were removed
            ax.set_xlabel('Democratic Party vote share (%)')
            y = data[0]
            x = np.random.normal(1, 0.04, size=len(y))
            ax.plot(x, y)
            plt.savefig(output_filename + '_Test2a.png')
            #            plt.show()
            print('<IMG SRC="%s_Test2a.png" border="0" alt="Logo"></p>\n<p></p>\n<p>' % output_filename, file=f1)

        else:
            print("Can't compare win margins. For this test, both parties must have at least two "
                  "seats.</p>\n<p></p>\n<p>", file=f1)

    if partisan_balance < 0.05:
        print("When one party is dominant statewide, it gains an overall advantage by spreading its strength as "
              "uniformly as possible across districts. The statistical test to detect an abnormally uniform pattern "
              "is the <a href=\"http://www.itl.nist.gov/div898/handbook/eda/section3/eda358.htm\">chi-square "
              "test</a>, in which the vote share of the majority party-controlled seats are compared with nationwide "
              "patterns.</p>\n<p></p>\n<p>",
              file=f1)
        # chi square test on majority of delegation
        if len(d_districts) > len(r_districts):
            var_compare = np.var(national_results[national_results > 0.5])
            p2b = var_test(list(state_results.tolist()[i] for i in d_districts), var_compare)
            std_value = np.std(list(state_results.tolist()[i] for i in d_districts) * 100, ddof=1)
            var_value = np.sqrt(var_compare) * 100
            print('The standard deviation of the Democratic majority''s winning vote share is %2.1f %%. ' % std_value,
                  file=f1)
            print('At a national level, the standard deviation is %2.1f %%. ' % var_value, file=f1)
        else:
            data_1 = national_results[national_results < 0.5]
            var_compare = np.var(data_1, ddof=1)
            p2b = var_test(list(state_results.tolist()[i] for i in r_districts), var_compare)
            std_value = np.std(list(state_results.tolist()[i] for i in r_districts), ddof=1) * 100
            var_value = np.sqrt(var_compare) * 100
            print('The standard deviation of the Republican majority''s winning vote share is {:2.1f} %. '.format(
                std_value), file=f1)
            print('At a national level, the standard deviation is %2.1f %%. ' % var_value, file=f1)

        if p2b < 0.01:
            print("This difference is statistically significant (p<0.01), and in a case of suspected gerrymandering is "
                  "extremely unlikely to have arisen by chance. ",
                  file=f1)
        elif p2b < 0.05:
            print('This difference is statistically significant (p<0.05), and in a case of suspected gerrymandering is '
                  'unlikely to have arisen by chance. ',
                  file=f1)
        else:
            print('This difference is not statistically significant (p>0.05). ', file=f1)

        print('</p>\n<p>', file=f1)

    # labels = state_name
    #        data = [df_state_raw['D_voteshare']]
    #        color = list(df_state_raw['pol'])

    # fig = plt.figure() fig.subtitle('Analysis of Intents: Chi-square test for unusually uniform outcomes',
    # fontsize=10, fontweight='bold') ax = fig.add_subplot(111) ax.boxplot(data, 0, 'ro', 0, labels=labels,
    # showfliers=True, showmeans=True) ax.set_xlabel('Districts (sorted by vote share)') ax.set_ylabel('Democratic
    # vote share (%)') plt.savefig(output_filename + '_Test2b.png') plt.show() print('<IMG SRC="%s_Test2b.png"
    # border="0" alt="Logo"></p>\n<p>' % output_filename, file=f1)

    f1.close()

    #    % JPEG: show bar plot of all districts
    #    % inset message, SD of majority district vote share, compare with national SD
    #        Fig2b = figure(3);
    #        set(Fig2b, 'Position', [600 100 600 300])
    #        title('Analysis of Intents: Chi-square test for unusually uniform outcomes')
    #        hold on
    #    % plot zone of chance for majority?
    #        plot([0 length(d_districts)+length(r_districts)+0.5],[50 50],'-k');
    #        if length(d_districts)>0
    #            bar([1:length(d_districts)],100*state_raw(d_districts),'b')
    #        end
    #        if length(r_districts)>0
    #            bar([length(d_districts)+1:length(d_districts)+length(r_districts)],100*state_raw(r_districts),'r')
    #        end
    #        axis([0 length(d_districts)+length(r_districts)+0.5 -3 100]);
    #        x_label('Districts (sorted by vote share)')
    #        y_label('Democratic vote share (%)')
    #        set(gca,'XTick',[]);
    #        set(gca,'YTick',[0 10 20 30 40 50 60 70 80 90 100]);
    #
    #        set(gcf,'PaperPositionMode','auto')
    #        print([output_filename '_Test2b_hires.jpg'],'-djpeg','-r300')
    #        screen2jpeg([output_filename '_Test2b.jpg'])#
    #
    #        fprintf(fid,'<IMG SRC="%s_Test2b.jpg" border="0" alt="Logo"></p>\n<p></p>\n',output_filename);
    #    end
    #    results=1;
    # end


# import pylab as P
# import numpy as np
# P.figure()
# P.xlim([0,2])
# y = data[0]
# x_temp = np.ones(len(y))
# P.plot(x_temp, y, 'r.', color = 'red')
# y = data[1]
# x_temp = np.ones(len(y))
# P.plot(x_temp, y, 'r.', color = 'blue')
# P.show()

gerrymander_tests_part1(2016, 3, 2016, 0, 0.75, 0, 'Arizona', 'foo')
